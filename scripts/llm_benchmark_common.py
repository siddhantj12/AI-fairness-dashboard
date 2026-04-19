"""
llm_benchmark_common.py

Shared helpers for qualitative-only LLM fairness benchmarking.
"""
from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd

from qualitative_analysis import (
    _get_attr_metrics,
    classify_severity,
    detect_proxy_features,
    diagnose_imbalance,
    map_root_causes,
    per_group_breakdown,
)
from scholarly_evidence import build_attribute_queries, gather_research_context

REFERENCE_AUDIT_SPEC = {
    "name": "Reference Audit Specification",
    "core_metrics": [
        "Disparate Impact",
        "Demographic Parity Difference",
        "Equal Opportunity Difference",
        "Average Odds Difference",
        "Theil Index",
    ],
    "required_response_elements": [
        "per-group breakdown",
        "severity classification",
        "root-cause analysis",
        "mitigation recommendations",
        "research-backed justification",
    ],
    "why_this_spec": (
        "A remediation-ready fairness audit should combine quantitative disparity "
        "measurement with interpretable causes, explicit severity, and concrete "
        "recommended interventions."
    ),
}

ALGORITHM_KEYWORDS = [
    "reweighing",
    "disparateimpactremover",
    "prejudiceremover",
    "eqoddspostprocessing",
    "calibratedeqoddspostprocessing",
    "exponentiatedgradient",
    "gridsearch",
    "thresholdoptimizer",
    "equalized odds",
    "adversarial debiasing",
    "fairness constraint",
    "demographic parity constraint",
]

# Actionability: terms that indicate concrete, implementable steps
ACTIONABILITY_KEYWORDS = [
    "implement", "apply", "configure", "train with", "deploy",
    "pipeline", "threshold", "parameter", "regularization",
    "class_weight", "retrain", "cross-validation", "held-out",
    "validation set", "schedule", "quarterly", "monthly", "annually",
    "set ", "step ", "target n", "repair_level",
]

# Governance: terms that indicate monitoring, auditing, or policy compliance
GOVERNANCE_KEYWORDS = [
    "monitor", "audit", "review", "dashboard", "alert", "report",
    "document", "compliance", "governance", "policy", "oversight",
    "periodic", "quarterly", "annual", "log ", "track", "measure",
    "re-audit", "re-evaluate", "drift", "flag", "intersectional",
]

CAUSE_LABELS = {
    "historical / label bias": "historical_label_bias",
    "proxy discrimination": "proxy_discrimination",
    "representation bias": "representation_bias",
    "unequal opportunity": "unequal_opportunity",
    "unequal odds": "unequal_odds",
}

# Scoring rubric version tag — increment when rubric changes
RUBRIC_VERSION = "v2"


def build_context_and_baseline(
    predictions_df: pd.DataFrame,
    fairness_df: pd.DataFrame,
    protected_configs: dict[str, str],
    target_col: str,
    pred_col: str,
    favorable_label: int,
    dataset_name: str,
    threshold: float = 0.8,
) -> tuple[dict[str, Any], dict[str, Any], list[dict[str, Any]]]:
    """Build shared quantitative context and deterministic qualitative baseline."""
    protected_attrs = list(protected_configs.keys())
    non_feature = {target_col, pred_col, "actual", "predicted"} | set(protected_attrs)
    feature_cols = [c for c in predictions_df.columns if c not in non_feature]

    dataset_research = gather_research_context(
        dataset_name=dataset_name,
        protected_attrs=protected_attrs,
        max_papers=6,
    )

    context_attrs: list[dict[str, Any]] = []
    baseline_attrs: list[dict[str, Any]] = []

    for attr, privileged_value in protected_configs.items():
        metrics = _get_attr_metrics(fairness_df, attr)
        breakdown = per_group_breakdown(predictions_df, attr, target_col, pred_col, favorable_label)
        imbalance = diagnose_imbalance(breakdown, attr)
        di = metrics.get("DisparateImpact")
        dpd = metrics.get("DemographicParityDiff")
        eod = metrics.get("EqualOpportunityDiff")
        aod = metrics.get("AverageOddsDiff")
        theil = metrics.get("TheilIndex")
        severity = classify_severity(di, threshold)

        context_attrs.append({
            "attribute": attr,
            "privileged_value": str(privileged_value),
            "metrics": {
                "disparate_impact": _safe_num(di),
                "demographic_parity_diff": _safe_num(dpd),
                "equal_opportunity_diff": _safe_num(eod),
                "average_odds_diff": _safe_num(aod),
                "theil_index": _safe_num(theil),
            },
            "group_breakdown": breakdown.to_dict(orient="records"),
            "imbalance_findings": imbalance,
            "severity_thresholds": {
                "critical_if_di_below": round(threshold * 0.9, 2),
                "high_if_di_below": threshold,
                "moderate_if_di_below": 0.95,
            },
        })

        proxies = detect_proxy_features(predictions_df, attr, feature_cols)
        root = map_root_causes(di, dpd, eod, aod, imbalance, proxies, breakdown, threshold)
        attr_research = gather_research_context(
            dataset_name=dataset_name,
            protected_attrs=[attr],
            extra_queries=build_attribute_queries(dataset_name, attr, root["causes"], root["fixes"]),
            max_papers=3,
            causes=root["causes"],
            fixes=root["fixes"],
        )
        baseline_attrs.append({
            "attribute": attr,
            "severity": severity,
            "root_cause_labels": _extract_cause_labels(root["causes"]),
            "root_causes": root["causes"],
            "mitigations": root["fixes"],
            "research_titles": [paper["title"] for paper in attr_research],
        })

    context_payload = {
        "dataset_name": dataset_name,
        "favorable_label": favorable_label,
        "reference_audit_spec": REFERENCE_AUDIT_SPEC,
        "attributes": context_attrs,
    }
    baseline_payload = {
        "reference_audit_spec": REFERENCE_AUDIT_SPEC,
        "attributes": baseline_attrs,
    }
    return context_payload, baseline_payload, dataset_research


def build_score_summary(score: dict[str, Any]) -> str:
    s = score["subscores"]
    mit = s.get("mitigation_quality", s.get("mitigation_specificity", 0.0))
    return (
        f"Total score: {score['total_score']:.1f}/100 [{RUBRIC_VERSION}]. "
        f"Completeness={s['completeness']:.1f}/35, "
        f"Severity agreement={s['severity_agreement']:.1f}/20, "
        f"Cause alignment={s['cause_alignment']:.1f}/15, "
        f"Mitigation quality={mit:.1f}/20, "
        f"Research grounding={s['research_grounding']:.1f}/10."
    )


def score_llm_output(result: dict[str, Any], baseline_payload: dict[str, Any]) -> dict[str, Any]:
    """Score a qualitative LLM output against the deterministic baseline.

    Rubric v2 (total = 100 pts):
        Completeness        35 pts
        Severity agreement  20 pts
        Cause alignment     15 pts
        Mitigation quality  20 pts  (algorithm 8 + actionability 6 + governance 6)
        Research grounding  10 pts
    """
    baseline_by_attr = {
        row["attribute"]: row for row in baseline_payload.get("attributes", [])
    }
    result_by_attr = {
        row["attribute"]: row for row in result.get("qualitative", [])
    }

    completeness = _score_completeness(result, expected_attrs=list(baseline_by_attr.keys()))
    severity_agreement = _score_severity(result_by_attr, baseline_by_attr)
    cause_alignment = _score_cause_alignment(result_by_attr, baseline_by_attr)
    mitigation_quality, mit_subscores = _score_mitigation_quality(result_by_attr)
    research_grounding = _score_research_grounding(result, result_by_attr)

    total = completeness + severity_agreement + cause_alignment + mitigation_quality + research_grounding
    subscores = {
        "completeness": round(completeness, 2),
        "severity_agreement": round(severity_agreement, 2),
        "cause_alignment": round(cause_alignment, 2),
        "mitigation_quality": round(mitigation_quality, 2),
        "mitigation_subscores": {k: round(v, 2) for k, v in mit_subscores.items()},
        "research_grounding": round(research_grounding, 2),
    }
    return {
        "total_score": round(total, 2),
        "rubric_version": RUBRIC_VERSION,
        "subscores": subscores,
        "summary": build_score_summary({"total_score": total, "subscores": subscores}),
    }


def _extract_cause_labels(causes: list[str]) -> list[str]:
    labels: list[str] = []
    for cause in causes:
        lower = cause.lower()
        for phrase, label in CAUSE_LABELS.items():
            if phrase in lower:
                labels.append(label)
    return sorted(set(labels))


def _normalize_severity(value: str) -> str:
    value = (value or "").upper()
    for label in ["CRITICAL", "HIGH", "MODERATE", "LOW"]:
        if label in value:
            return label
    return value.strip() or "UNKNOWN"


def _score_completeness(result: dict[str, Any], expected_attrs: list[str]) -> float:
    """Completeness of reference audit spec and attribute coverage (max 35 pts)."""
    score = 0.0
    spec = result.get("reference_audit_spec", {})
    if spec.get("name"):
        score += 4
    if len(spec.get("core_metrics", [])) >= 4:
        score += 7
    if len(spec.get("required_response_elements", [])) >= 4:
        score += 7
    if spec.get("why_this_spec"):
        score += 5
    if len(spec.get("supporting_research", [])) >= 2:
        score += 4

    qualitative = result.get("qualitative", [])
    result_attrs = {row.get("attribute") for row in qualitative}
    if set(expected_attrs).issubset(result_attrs):
        score += 8
    return min(score, 35.0)


def _score_severity(result_by_attr: dict[str, dict[str, Any]], baseline_by_attr: dict[str, dict[str, Any]]) -> float:
    if not baseline_by_attr:
        return 0.0
    matches = 0
    for attr, baseline in baseline_by_attr.items():
        got = result_by_attr.get(attr, {})
        if _normalize_severity(got.get("severity", "")) == _normalize_severity(baseline.get("severity", "")):
            matches += 1
    return 20.0 * (matches / len(baseline_by_attr))


def _score_cause_alignment(result_by_attr: dict[str, dict[str, Any]], baseline_by_attr: dict[str, dict[str, Any]]) -> float:
    if not baseline_by_attr:
        return 0.0
    matched = 0
    total = 0
    for attr, baseline in baseline_by_attr.items():
        why = (result_by_attr.get(attr, {}).get("why_is_wrong", "") or "").lower()
        labels = baseline.get("root_cause_labels", [])
        for label in labels:
            total += 1
            plain = label.replace("_", " ")
            if plain in why:
                matched += 1
    if total == 0:
        return 10.0
    return 15.0 * (matched / total)


def _score_mitigation_quality(
    result_by_attr: dict[str, dict[str, Any]],
) -> tuple[float, dict[str, float]]:
    """Score mitigation quality across three dimensions (max 20 pts total).

    Dimensions:
        Algorithm specificity  8 pts — names a known fairness algorithm
        Actionability          6 pts — contains concrete implementation steps
        Governance             6 pts — includes monitoring / compliance language
    """
    if not result_by_attr:
        return 0.0, {"algorithm_specificity": 0.0, "actionability": 0.0, "governance": 0.0}

    algo_hits = action_hits = gov_hits = 0
    n = len(result_by_attr)

    for row in result_by_attr.values():
        raw = (row.get("how_to_fix", "") or "").lower()
        text_norm = raw.replace("-", "").replace("_", "")

        if any(k.replace("-", "").replace("_", "") in text_norm for k in ALGORITHM_KEYWORDS):
            algo_hits += 1
        if any(k in raw for k in ACTIONABILITY_KEYWORDS):
            action_hits += 1
        if any(k in raw for k in GOVERNANCE_KEYWORDS):
            gov_hits += 1

    algo_score = 8.0 * (algo_hits / n)
    action_score = 6.0 * (action_hits / n)
    gov_score = 6.0 * (gov_hits / n)
    total = algo_score + action_score + gov_score
    return total, {
        "algorithm_specificity": algo_score,
        "actionability": action_score,
        "governance": gov_score,
    }


def _score_research_grounding(result: dict[str, Any], result_by_attr: dict[str, dict[str, Any]]) -> float:
    score = 0.0
    if len(result.get("reference_audit_spec", {}).get("supporting_research", [])) >= 2:
        score += 5
    attr_hits = 0
    for row in result_by_attr.values():
        if len(row.get("supporting_research", [])) >= 1:
            attr_hits += 1
    if result_by_attr:
        score += 10.0 * (attr_hits / len(result_by_attr))
    return score


def _safe_num(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

