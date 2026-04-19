"""
scholarly_evidence.py

Shared Semantic Scholar helpers for fairness benchmarking and reporting.

These helpers intentionally use only the Python standard library so they can be
used from any pipeline step without adding new dependencies.

Citation credibility policy (year-aware):
    ≤ 2 years old  → 0 citations required  (insufficient time to accumulate)
    3–4 years old  → 3 citations required   (recent, low bar)
    5–7 years old  → 10 citations required  (established, moderate bar)
    8+ years old   → 20 citations required  (older work must be well-established)

Relevance policy:
    Each paper is scored by how many cause/fix/query terms appear in its
    title + abstract.  Papers with relevance_score == 0 are discarded;
    within each credibility tier, papers are ranked by relevance first,
    citation count second.
"""
from __future__ import annotations

import datetime
import json
import logging
import os
import re
import time
import urllib.parse
import urllib.error
import urllib.request
from typing import Any

log = logging.getLogger(__name__)

SEMANTIC_SCHOLAR_API = "https://api.semanticscholar.org/graph/v1/paper/search"
DEFAULT_FIELDS = (
    "title,year,authors,abstract,url,venue,citationCount,externalIds,paperId"
)
REQUEST_INTERVAL_S = 1.1
MAX_RETRIES = 3
_LAST_REQUEST_TS = 0.0

# Current year used for age-based citation thresholds
_CURRENT_YEAR: int = datetime.datetime.now().year

# Venues that receive a relevance bonus (well-known fairness/ML venues)
_FAIRNESS_VENUES: frozenset[str] = frozenset({
    "facct", "fatml", "aies", "fat*", "fat ", "neurips", "nips",
    "icml", "iclr", "aaai", "ijcai", "acl", "emnlp", "kdd",
    "www", "wsdm", "ecml", "sigkdd", "acm conference",
})

# Core domain terms always considered relevant
_CORE_FAIRNESS_TERMS: frozenset[str] = frozenset({
    "fairness", "fair", "bias", "disparity", "discrimination",
    "mitigation", "disparate", "parity", "equalized", "reweigh",
    "proxy", "representation", "algorithmic", "protected", "sensitive",
    "privileged", "unprivileged", "subgroup", "demographic",
})


def _respect_rate_limit() -> None:
    global _LAST_REQUEST_TS
    now = time.monotonic()
    wait_s = REQUEST_INTERVAL_S - (now - _LAST_REQUEST_TS)
    if wait_s > 0:
        time.sleep(wait_s)
    _LAST_REQUEST_TS = time.monotonic()


def _year_aware_citation_threshold(year: int | None) -> int:
    """Minimum credible citation count for a paper of this age.

    Newer papers haven't had time to accumulate citations, so we exempt them
    from the credibility threshold entirely. Older work must be well-cited to
    be considered credible.
    """
    if year is None:
        return 5  # unknown year: conservative default
    age = _CURRENT_YEAR - int(year)
    if age <= 2:    # e.g. 2024–2026: very recent, no requirement
        return 0
    if age <= 4:    # e.g. 2022–2023: recent, low bar
        return 3
    if age <= 7:    # e.g. 2019–2021: established, moderate bar
        return 10
    return 20       # 2018 and older: must be well-established


def _credibility_tier(year: int | None, citation_count: int) -> str:
    """Human-readable credibility tier for reporting."""
    threshold = _year_aware_citation_threshold(year)
    if threshold == 0:
        return "recent (no citation requirement)"
    if citation_count >= threshold * 3:
        return "high (well-cited)"
    if citation_count >= threshold:
        return "adequate (meets threshold)"
    return "low (below threshold)"


def _extract_relevance_terms(
    query: str,
    causes: list[str] | None = None,
    fixes: list[str] | None = None,
    attr: str | None = None,
) -> set[str]:
    """Build a set of meaningful terms for relevance scoring.

    Returns lowercase single-word tokens (≥ 4 chars) and bigrams extracted
    from the query, causes, and fixes, plus core fairness vocabulary.
    """
    terms: set[str] = set(_CORE_FAIRNESS_TERMS)

    def _tokenize(text: str) -> list[str]:
        words = re.findall(r"[a-z]{4,}", text.lower())
        bigrams = [f"{words[i]} {words[i+1]}" for i in range(len(words) - 1)]
        return words + bigrams

    for source in ([query] + (causes or []) + (fixes or [])):
        terms.update(_tokenize(source))

    # Protected attribute name itself is always relevant
    if attr:
        terms.update(_tokenize(attr))

    # Remove very common English stop-words that are not domain-specific
    _stopwords = {"that", "this", "with", "from", "have", "will", "more",
                  "than", "they", "their", "been", "also", "such", "each",
                  "when", "then", "into", "over", "after", "before"}
    terms -= _stopwords
    return terms


def _relevance_score(paper: dict[str, Any], terms: set[str]) -> int:
    """Count how many relevance terms appear in the paper's title + abstract + venue."""
    text = (
        (paper.get("title") or "").lower() + " "
        + (paper.get("abstract") or "").lower()
    )
    score = sum(1 for t in terms if t in text)

    # Bonus for being in a known fairness/ML venue
    venue = (paper.get("venue") or "").lower()
    if any(fv in venue for fv in _FAIRNESS_VENUES):
        score += 3

    return score


def search_semantic_scholar(
    query: str,
    limit: int = 3,
    fields: str = DEFAULT_FIELDS,
    timeout_s: int = 20,
) -> list[dict[str, Any]]:
    """Return simplified Semantic Scholar search results for a query."""
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": fields,
    })
    req = urllib.request.Request(f"{SEMANTIC_SCHOLAR_API}?{params}")
    req.add_header("User-Agent", "AI-Fairness-Dashboard/1.0")

    api_key = os.getenv("SEMANTIC_SCHOLAR_API_KEY")
    if api_key:
        req.add_header("x-api-key", api_key)

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            _respect_rate_limit()
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                payload = json.loads(resp.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as exc:
            if exc.code == 429 and attempt < MAX_RETRIES:
                wait_s = REQUEST_INTERVAL_S * (2 ** attempt)
                log.warning(
                    f"Semantic Scholar rate limited for '{query}'. Retrying in {wait_s:.1f}s ..."
                )
                time.sleep(wait_s)
                continue
            log.warning(f"Semantic Scholar query failed for '{query}': {exc}")
            return []
        except Exception as exc:
            log.warning(f"Semantic Scholar query failed for '{query}': {exc}")
            return []

    papers: list[dict[str, Any]] = []
    for item in payload.get("data", []):
        papers.append({
            "paper_id": item.get("paperId"),
            "title": item.get("title") or "Untitled",
            "year": item.get("year"),
            "venue": item.get("venue"),
            "citation_count": item.get("citationCount", 0),
            "url": item.get("url"),
            "abstract": item.get("abstract") or "",
            "authors": [a.get("name", "") for a in item.get("authors", [])[:5]],
            "query": query,
        })
    return papers


def build_default_queries(
    dataset_name: str,
    protected_attrs: list[str] | tuple[str, ...],
) -> list[str]:
    attrs = ", ".join(protected_attrs[:3]) if protected_attrs else "protected attributes"
    return [
        "algorithmic fairness bias detection mitigation machine learning",
        "AIF360 fairlearn bias mitigation demographic parity equal opportunity",
        "proxy discrimination machine learning fairness sample size subgroup reliability",
        f"{dataset_name} fairness bias mitigation {attrs}",
    ]


def build_attribute_queries(
    dataset_name: str,
    attr: str,
    causes: list[str],
    fixes: list[str],
) -> list[str]:
    queries = [
        f"{dataset_name} fairness {attr} bias mitigation",
        f"{attr} proxy discrimination machine learning fairness",
    ]

    joined_causes = " ".join(causes).lower()
    joined_fixes = " ".join(fixes).lower()

    if "historical / label bias" in joined_causes or "historical bias" in joined_causes:
        queries.append("historical label bias fairness machine learning mitigation")
    if "proxy discrimination" in joined_causes or "proxy" in joined_causes:
        queries.append("proxy discrimination fairness machine learning mitigation")
    if "representation bias" in joined_causes or "imbalance" in joined_causes:
        queries.append("subgroup sample size reliability fairness machine learning")

    if "reweigh" in joined_fixes:
        queries.append("reweighing fairness machine learning")
    if "thresholdoptimizer" in joined_fixes or "equalized odds" in joined_fixes:
        queries.append("equalized odds postprocessing fairness machine learning")
    if "prejudice remover" in joined_fixes:
        queries.append("prejudice remover fair classification")
    if "disparate impact remover" in joined_fixes:
        queries.append("disparate impact remover preprocessing fairness")

    return queries


def gather_research_context(
    dataset_name: str,
    protected_attrs: list[str] | tuple[str, ...],
    extra_queries: list[str] | None = None,
    max_papers: int = 6,
    per_query_limit: int = 3,
    causes: list[str] | None = None,
    fixes: list[str] | None = None,
    min_relevance_score: int = 1,
) -> list[dict[str, Any]]:
    """Collect papers with year-aware citation credibility and relevance filtering.

    Selection pipeline:
        1. Fetch candidates from all queries (default + attribute-specific).
        2. Deduplicate by paper_id (or title fallback).
        3. Discard papers with relevance_score < min_relevance_score.
        4. Apply year-aware citation threshold:
               age ≤ 2 yrs → 0 citations required
               age 3–4 yrs → 3 citations required
               age 5–7 yrs → 10 citations required
               age 8+ yrs  → 20 citations required
        5. Split into credible (meets threshold) and recent-only (exempt by age).
        6. Sort each bucket by (relevance_score DESC, citation_count DESC).
        7. Fill up to max_papers from credible first, then recent-only.

    Each returned paper carries:
        relevance_score    int  — count of matching terms in title + abstract
        meets_credibility  bool — passed the year-aware citation threshold
        credibility_tier   str  — human-readable tier label for reporting
        citation_threshold int  — threshold that was applied to this paper
    """
    queries = build_default_queries(dataset_name, protected_attrs)
    if extra_queries:
        queries.extend(extra_queries)
    queries = list(dict.fromkeys(queries))

    # Build a shared relevance term set from all queries + causes + fixes
    all_query_text = " ".join(queries)
    attr_hint = " ".join(str(a) for a in protected_attrs)
    relevance_terms = _extract_relevance_terms(
        all_query_text,
        causes=causes,
        fixes=fixes,
        attr=attr_hint,
    )

    seen: set[str] = set()
    credible: list[dict[str, Any]] = []   # meets year-aware threshold
    recent_only: list[dict[str, Any]] = []  # exempt because age ≤ 2 yrs
    irrelevant_dropped = 0
    below_threshold_dropped = 0

    for query in queries:
        if len(credible) >= max_papers:
            break
        for paper in search_semantic_scholar(query, limit=per_query_limit):
            key = paper.get("paper_id") or paper.get("title", "").lower()
            if not key or key in seen:
                continue
            seen.add(key)

            year = paper.get("year")
            cites = int(paper.get("citation_count", 0) or 0)
            threshold = _year_aware_citation_threshold(year)
            age = (_CURRENT_YEAR - int(year)) if year else None

            # Annotate paper with credibility metadata
            paper["citation_threshold"] = threshold
            paper["meets_credibility"] = cites >= threshold
            paper["credibility_tier"] = _credibility_tier(year, cites)

            # Compute and annotate relevance
            rscore = _relevance_score(paper, relevance_terms)
            paper["relevance_score"] = rscore

            # Discard papers with no relevance signal
            if rscore < min_relevance_score:
                irrelevant_dropped += 1
                log.debug(
                    "Dropped irrelevant paper (score=%d): %s",
                    rscore,
                    paper.get("title", "")[:60],
                )
                continue

            if paper["meets_credibility"]:
                credible.append(paper)
            elif age is not None and age <= 2:
                # Recent papers pass even with 0 citations
                recent_only.append(paper)
            else:
                # Older paper that doesn't meet its citation threshold
                below_threshold_dropped += 1
                log.debug(
                    "Dropped low-credibility paper (%d cites, threshold=%d, age=%s yr): %s",
                    cites, threshold, age,
                    paper.get("title", "")[:60],
                )

    # Sort each bucket: relevance first, then citation count
    def _sort_key(p: dict) -> tuple:
        return (p.get("relevance_score", 0), int(p.get("citation_count", 0) or 0))

    credible.sort(key=_sort_key, reverse=True)
    recent_only.sort(key=_sort_key, reverse=True)

    papers = credible[:max_papers]
    if len(papers) < max_papers:
        papers.extend(recent_only[: max_papers - len(papers)])

    if irrelevant_dropped or below_threshold_dropped:
        log.info(
            "Semantic Scholar for '%s': kept %d papers, dropped %d irrelevant, "
            "%d below year-adjusted citation threshold.",
            dataset_name,
            len(papers),
            irrelevant_dropped,
            below_threshold_dropped,
        )

    return papers


def _trim(text: str, limit: int = 220) -> str:
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    return text[: limit - 3].rstrip() + "..."


def format_evidence_for_prompt(papers: list[dict[str, Any]]) -> str:
    """Render papers as a compact context block for an LLM prompt."""
    if not papers:
        return "No external research evidence was retrieved."

    lines = []
    for idx, paper in enumerate(papers, 1):
        authors = ", ".join(paper.get("authors", [])[:3]) or "Unknown authors"
        year = paper.get("year") or "n.d."
        venue = paper.get("venue") or "Unknown venue"
        cites = paper.get("citation_count", 0)
        tier = paper.get("credibility_tier", "")
        abstract = _trim(paper.get("abstract", ""))
        lines.append(
            f"[{idx}] {paper.get('title', 'Untitled')} ({year}) | {authors} | "
            f"{venue} | citations={cites} | credibility={tier}\n"
            f"    Summary: {abstract}"
        )
    return "\n".join(lines)


def format_evidence_markdown(
    papers: list[dict[str, Any]],
    heading: str = "### Research-backed evidence",
) -> list[str]:
    """Render papers as markdown lines for deterministic reports."""
    lines = [heading, ""]
    if not papers:
        lines.append("No external research evidence was retrieved for this section.")
        lines.append("")
        return lines

    for idx, paper in enumerate(papers, 1):
        authors = ", ".join(paper.get("authors", [])[:3]) or "Unknown authors"
        year = paper.get("year") or "n.d."
        venue = paper.get("venue") or "Unknown venue"
        cites = paper.get("citation_count", 0)
        tier = paper.get("credibility_tier", "")
        rscore = paper.get("relevance_score", "n/a")
        lines.append(
            f"{idx}. **{paper.get('title', 'Untitled')}** ({year}), {authors}. "
            f"*{venue}*. Citations: {cites} | Credibility: {tier} | Relevance score: {rscore}."
        )
        if paper.get("abstract"):
            lines.append(f"   {_trim(paper['abstract'])}")
        if paper.get("url"):
            lines.append(f"   {paper['url']}")
    lines.append("")
    return lines
