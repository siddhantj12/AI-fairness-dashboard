# Argument skeleton — report_facct.tex

Per-paragraph list of the arguments the paper *must* make. Anything in a
paragraph that does not serve one of its bullets is a cut candidate. Structure
matches the FAccT-standard scaffold (Introduction / Related Work / Methods /
Results / Discussion / Recommendations / Limitations / Conclusion) introduced
in the 2026-09 restructure; section labels in parentheses are stable.

Rule of thumb used throughout: each bullet is an argument, not a topic. If a
paragraph's bullets can be said in fewer sentences than the paragraph has,
shrink the paragraph.

---

## Abstract

- The same model on the same applicants passes or fails depending on settings
  invisible in the audit's output; every such setting is one event — named
  construct ≠ operationalised construct, output clean either way.
- The settings live at three layers (library, construct mapping, the audit's
  own instruments), each with one headline number.
- Verdicts are properties of model + unrecorded configuration; the fix is to
  ship the configuration like error bars (the six-item record).

**Cut candidate:** the abstract currently narrates all ten instances; two per
layer is enough — the inventory table does the rest.

## 1. Introduction

**¶1 (lending as the site).**
- Lending is where the named-vs-operationalised gap becomes *measurable*
  rather than arguable: the domain ships written definitions and dedicated
  flags.
- (Keep one framing citation; the Lee et al. sentence can compress to a
  clause.)

**¶2 (the claim).**
- The gap appears at every layer, takes the same shape at each, and is
  invisible in the output.
- Table 1 *is* the paper: every instance, named construct, operationalisation,
  clean number.

**¶3 (positioning).**
- Prior work already shows instruments and pipelines are part of the finding;
  our addition is a setting where the gap can be measured against published
  definitions.

**¶4 (contributions).**
- Five contributions, one clause each, each pointing at a section. Already
  tight; keep.

## 2. Related Work (sec:background)

**¶1 (measurement).**
- Fairness quantities are measurement models of unobservable constructs;
  construct validity is the question to ask of any number (Jacobs & Wallach).
- Intersectionality names the construct the race×sex cells operationalise.
- **Cut candidate:** this paragraph is a citation forest; the
  incompatibility-results sentence (Chouldechova/Kleinberg/Hardt) can be one
  clause — it is background to background.

**¶2 (the documented decision context).**
- We make no legal claims; what the domain supplies is narrower and
  sufficient: written definitions and published flags make the gap a
  checkable measurement question.
- Input scrutiny vs. outcome scrutiny are different measurements (sets up
  sec:treatment).

**¶3 (the audit's instruments).**
- LLM-judge fragility and prompt sensitivity are known; the joint claim the
  literatures have not made: a detector, gate, or score *is* a measurement
  model with the same validity obligations as the metric it polices.
- The stakeholder line asks who should choose the criteria; we show the
  apparatus resolves several such questions before anyone is asked.

## 3. Methods (sec:apparatus)

**3.1 Settings and data.**
- Two regulated lending settings (German Credit n=1,000; HMDA Georgia
  n=10,978) plus one deliberately vacuous instrument-test setting.
- Lending Club's protected attribute is a coin flip — it exists to test the
  harness where verdicts are known to be meaningless; it is never treated as
  a lending sector.

**3.2 Deterministic metric layer.**
- Every number comes from deterministic code (AIF360 cross-checked against
  Fairlearn) with a fixed severity rule.
- Audits run on the full population via out-of-fold predictions, not a
  held-out split.
- **Cut candidate:** the Theil-index/schema footnote detail can move entirely
  to the footnote.

**3.3 LLM interpretation layer.**
- The model interprets, never computes; scoring is always against the
  deterministic label (one disclosed exception).

**3.4 Population construction.**
- 45.1% of the raw file is dropped before any metric runs, including all
  Race-Not-Available applicants: selection on the protected attribute,
  upstream of every number.

**3.5 The four-fifths screen.**
- 0.80 is an imported employment convention, used here only as a screen, and
  its own source text anticipates the small-n failure this paper measures.

## 4. Results

**4.1 Layer one: the library (sec:library).**
- ¶scope: claims are about the verified versions only.
- ¶favorable-label: a constructor default answers "which outcome is good";
  on a `loan_default` target it reports the disadvantaged group as favoured
  (DI 1.2072 vs. oriented 0.9862); scoped precisely — one constructor, the
  other API requires the answer.
  - The in-vivo case: our own harness produced CRITICAL/DI=0.0 where the
    oriented value is 0.9931; nothing was "misused."
- ¶no-uncertainty: neither library ships interval, n, or reference group;
  n=31 prints as authoritatively as n=4,019 (sets up 4.3).
- ¶comparison: nothing records the denominator (sets up 4.2.2).

**4.2 Layer two: the documented construct (sec:statute).**
- 4.2.1 Age: 40+ is imported from employment; the domain's boundary is 62+
  and the data ship the flag; banded age *cannot* represent it (bands
  straddle 62) — 0.9791/LOW vs. 0.8897, largest age disparity present.
  Honest note: verdict unchanged on this data; the *question* changed.
- 4.2.2 Comparator: reference-group convention moves every ratio 3–4 points
  and is recorded nowhere.
- 4.2.3 Inputs: a model consuming sex and age end-to-end produced a clean
  DI=0.8888; outcome-rate metrics are structurally silent about inputs — no
  ratio at any n could have flagged it. (Arguably the paper's sharpest
  single result; do not shorten.)

**4.3 Measurement validity (sec:validity).**
- 4.3.1 Intervals: the original split audit *inverted* the worst cell into
  the best (1.1504 on n=4 vs. 0.6734 population); with intervals, only the
  Black×Female/Male disparity (~0.86) survives — the point-estimate ranking
  demoted the only defensible finding to sixth and seventh.
  - Floors suppress exactly the least-populated (minority) groups —
    mechanism, not coincidence.
- 4.3.2 Subsampling study: at the audit size actually used, every policy
  that reports small cells is usually wrong (83.8–95.2% false clearance);
  floors never false-clear only because they never report the violating
  cells (and misidentify the worst group 100% of the time).
  - Floors trade clearance for silence; intervals trade decisiveness for
    honesty; shrinkage buys confidence with bias toward clearance.
  - The reporting policy is a policy about who becomes visible, and nothing
    in a reported ratio records it.

**4.4 Layer three: the audit's own instruments (sec:instruments).**
- ¶scope: findings are about our released harness; same event as layers one
  and two.
- 4.4.1 Refusal: "under 40 characters" flagged six *correct* answers —
  compliance with the brevity instruction was the trigger; the same detector
  fed a 19.79 score that permanently blocked a provider. Invalid measurement
  → durable governance decision. (Two paragraphs; the reanalysis detail can
  compress — the 14-vs-4 empty-record accounting can live in the appendix.)
- 4.4.2 Fabrication: 67% of "fabrications" are derivable restatements; the
  detector demotes the model that shows its work. Seven values remain honest
  candidates — keep the honesty note.
- 4.4.3 Mitigation: the gate fails exactly the cases where "collect more
  data" is the only defensible remedy.
- 4.4.4 Own thresholds: 0.72 = 0.80×0.9 has no provenance; two different
  floors coexisted in adjacent modules. We are in the inventory too.
- 4.4.5 Capability: a 75% agreement mean decomposes to 33/92/100 and tracks
  task difficulty, not capability; most of the published prompt-sensitivity
  spread (14.7 → 6.7) was our scorer punishing instructed brevity — the
  scorer and the refusal detector measured the same thing under two
  construct names.
  - Keep the disclosure that Track H rubric scores are excluded by the
    paper's own architecture rule.
  - **Cut candidate:** the temperature-parameter aside can drop to a
    footnote.

## 5. Discussion (sec:invisible)

**¶1.** The construct questions (favorable? protected? compared to whom? on
how much evidence? checked how?) are answered by default or not at all — so
each is settled privately, without record.

**¶2.** The asymmetry is directional: every measured error erred toward the
clean, reassuring direction, and clean results are the least re-examined.

**¶3.** Every mechanical proxy for judgement is an unlabeled policy, and each
punished the better answer exactly where judgement was most needed; the
failure class scales with automated evaluation.

**¶4.** Two of our own decisions belong in the catalogue: attrition (deciding
who counts as protected upstream of every number) and a division of labour
that protected every number and none of the operationalisations.

## 6. Recommendations (sec:protocol)

- Six items, each derived from a measured failure (favorable outcome as
  required argument; interval+n+reference beside every ratio; definitions
  bound to source; gates treated as hypotheses; population + disclosed
  construction; named reporting policy).
- Necessary, not sufficient: this is the screening step only; citing it as
  compliance evidence is misuse.

## 7. Limitations (sec:limitations)

One bullet each; already terse — keep:
- Mechanism-level, not prevalence-level findings.
- No human subjects (claims about readers untested on readers).
- No causal or legal claims.
- Model/data bounds (protected attrs as features; synthetic attribute; no
  credit score).
- Sampling confound in the LLM layer.
- Subsampling study measures *our* conventions; conservative intervals
  over-cover.

## 8. Conclusion

**¶1.** One sentence per layer, each naming its decisive unrecorded setting.

**¶2.** The gap is not closable (all measurement operationalises) but it is
*recordable*; everything in the record is technically easy and currently
optional — which is the problem.
