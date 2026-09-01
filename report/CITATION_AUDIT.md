# Citation audit — report_facct.tex / refs.bib

One line per citation: what it is, what the paper takes from it, why it
strengthens the case — and a verdict. Verdicts: **LOAD-BEARING** (the argument
leans on it), **SOLID** (right citation, right place), **CLUSTER** (cited once
in a bracket list, never engaged — survives only as field-coverage), **WEAK**
(record or fit problem, named). Usage claims are read directly from the tex;
each entry's registrar status is in `artifacts/consolidated/bib_verification.json`.

## The spine (the paper falls over without these)

- **jacobswallach2021** (FAccT '21) — "Measurement and Fairness"; supplies the
  paper's entire vocabulary (fairness metrics are measurement models; the
  question is construct validity); cited in the abstract-level framing and
  the intro's first paragraph. **LOAD-BEARING**
- **chen2018** (NeurIPS '18) — "Why Is My Classifier Discriminatory?"; the
  bias–variance decomposition that says what a subgroup estimate can support;
  backs §4.3 twice and the appendix estimator design. **LOAD-BEARING**
- **gillis2022** (Minn. L. Rev.) — "The Input Fallacy"; input scrutiny vs.
  outcome scrutiny as different measurements; the scholarly backbone of the
  paper's sharpest result (§4.2.3). Record is hand-attested (law review, no
  DOI) — form-weak, content-strong. **LOAD-BEARING**
- **obermeyer2019** (Science) — the canonical in-vivo proxy substitution
  (cost standing in for need); the one-line proof that construct substitution
  causes real-world harm. **LOAD-BEARING**
- **mei2025** (FAccT '25) — audit *pipelines* introduce pitfalls that change
  conclusions (ASR/aphasia); the closest prior work, and the differentiation
  point ("we add a setting where the gap is measurable"). **LOAD-BEARING**
- **wester2024** (CHI '24) — LLM denials of user requests; names the construct
  our refusal detector was *supposed* to measure (§4.4.1). **LOAD-BEARING**
- **sclar2024** (ICLR '24) — prompt-format sensitivity; names the construct
  our sensitivity comparison was supposed to measure, and the class of
  published claim our reanalysis qualifies (§4.4.5). **LOAD-BEARING**

## Audited objects and data (not optional)

- **aif360** (IBM JRD '19) — the library under audit; the favorable-label
  default is its constructor. **SOLID**
- **fairlearn** (MSR TR 2020-32) — the cross-check library; tech report is the
  standard citation for it. **SOLID**
- **germancredit** (UCI, 1994) — dataset source, DOI-registered. **SOLID**
- **hmda** (CFPB) — dataset source; also the provenance of the 62+ flag the
  age argument turns on. **SOLID**

## Direct supports (each does one named job)

- **passi2019** (FAT* '19) — locates the gap upstream in problem formulation;
  situates our layer story. **SOLID**
- **selbst2019** (FAT* '19) — porting formal criteria across contexts fails;
  underwrites the "imported construct" framing (40+, four-fifths). **SOLID**
- **barocas2021** (AIES '21) — disaggregated evaluation as a series of
  choices (which groups, cells, comparisons); the design-space our layer two
  instantiates. **SOLID**
- **crenshaw1989** (U. Chi. Legal Forum) — names intersectionality, the
  construct the race×sex cells operationalise; also part of the paper's own
  story (the automated bib gate once rejected it). **SOLID**
- **buolamwini2018** (FAT*/PMLR '18) — the canonical empirical intersectional
  audit; precedent for our cell tables. **SOLID**
- **barocas2016** (Cal. L. Rev. 104(3), 671–732) — "discrimination law does
  not reduce to a metric threshold"; half of the no-legal-claims stance.
  Record upgraded from the SSRN preprint to the published version on
  2026-09-01 (DOI resolved via DataCite). **SOLID**
- **wachter2021** (CLSR) — the EU half of the same stance; "fairness cannot be
  automated." **SOLID**
- **feldman2015** (KDD '15) — disparate impact removal; does double duty: the
  algorithm the terse *correct* answer named (§4.4.1) and a mitigation-gate
  keyword (§4.4.3). **SOLID**
- **kamiran2011** (KAIS) — reweighing, the other gate keyword. Minor: usually
  cited as 2012 (journal issue); DOI is online-first 2011. **SOLID**
- **deng2022** (FAccT '22) — practitioners use fairness toolkits in ways
  designers didn't anticipate; positioning for "the instrument is part of the
  finding." **SOLID**
- **leesingh2021** (CHI '21) — systematic gaps in what open-source toolkits
  support; same job, tool-side. **SOLID**
- **holstein2019** (CHI '19) — practitioner needs diverge from what the
  literature supplies; same job, practice-side. **SOLID**
- **zaccour2025** (CHI '25) — quantitative audits blocked by data access more
  than method; motivates the public-data setting. **SOLID**
- **zheng2023** (NeurIPS '23) — LLM-as-judge fragility; the reason Track H's
  rubric scores are excluded by our own rule (§4.4.5). **SOLID**
- **kroll2021** (FAccT '21) — traceability as an accountability principle; the
  rationale for the artifact map / released-artifact design. **SOLID**
- **zamfirescu2022** (FAccT '22) — diagnosing human error inside an analysis
  pipeline; the contrast that sharpens our claim ("we diagnose the pipeline's
  own rulers"). **SOLID**
- **luo2025** (PACMHCI) — EARN Fairness, stakeholders negotiating metrics;
  used twice, including the limitations section's "natural next study."
  **SOLID**
- **luo2026b** (arXiv preprint) — affected individuals shaping assessments;
  also reused in limitations, so it earns its place — but it is a preprint;
  check for a published version before submission. **SOLID, record WEAK**

## Settled-background brackets (fine as one clause; do not expand)

- **chouldechova2017** (Big Data) — impossibility result (calibration vs.
  error rates); one clause of settled background. **SOLID**
- **kleinberg2017** (ITCS '17) — the companion impossibility result; same
  clause. **SOLID**
- **hardt2016** (NeurIPS '16) — equalized odds; same clause; also the source
  concept behind the equal-opportunity difference metrics the pipeline
  computes. **SOLID**
- **corbettdavies2018** (arXiv) — measures mislead when detached from decision
  context; one clause. Superseded record: the published version is
  Corbett-Davies et al., JMLR 2023 (expanded author list) — cite that instead.
  **SOLID, record WEAK**

## Weak links (fix, trim, or accept knowingly)

- **butler2017** (Mgmt. Sci.) — local capital-market conditions and borrowing
  decisions; cited inside the "lending discrimination is documented" bracket,
  but the paper is about credit access conditions, not discrimination —
  miscast for the claim it currently supports; move it or drop it. **WEAK
  (fit)**
- **sarwal2024** (harvested record) — pipeline-harvested lending-bias paper;
  venue field is malformed (a congress name in a `journal` field), it resolves
  through no registrar, and it is attested only by the pipeline's own
  evidence file; it survives as provenance-honesty (the pipeline cited it, so
  the paper discloses it), not as support — the weakest record in the file.
  **WEAK (record)**
- **kim2025** (PACMHCI) — equity lit review; appears once inside the
  stakeholder bracket, never engaged. **CLUSTER**
- **luo2026** (CHI '26) — stakeholder decision-making complexity; bracket-only,
  and luo2025/luo2026b already carry this line; a cut candidate. **CLUSTER**
- **deshpande2022** (AIES '22) — who are the stakeholders; bracket-only.
  **CLUSTER**
- **stumpf2024** (UMAP Adjunct '24) — user-centred fairness assessment;
  bracket-only *and* an adjunct-proceedings venue — the weakest of the
  stakeholder cluster. **CLUSTER, venue WEAK**
- **foulds2020** (ICDE '20) — formal intersectional fairness definition;
  bracket-only; standard but unengaged. **CLUSTER**
- **kearns2018** (ICML '18) — subgroup-fairness auditing theory; currently
  bracket-only, which is a missed opportunity rather than padding: it is the
  theoretical frame for the small-cell/subgroup problem §4.3 measures — either
  engage it in one sentence there or accept it as cluster. **CLUSTER
  (under-used)**
- **metaxa2021** (FnT HCI) — external algorithm audits survey; one list with
  raji2019/raji2020; three citations where two would do. **CLUSTER**
- **raji2019** (AIES '19) — actionable auditing (public naming changes
  behavior); same list; the most cuttable of the three. **CLUSTER**
- **raji2020** (FAT* '20) — internal audit framework ending in documented
  artifacts; same list, but the most relevant of the three to the six-item
  record — keep this one if trimming. **SOLID**
- **mitchell2019** (FAT* '19) — model cards; documentation-intervention
  premise; one list with gebru2021/madaio2020. **SOLID**
- **gebru2021** (CACM) — datasheets; same list; keep (the record's closest
  ancestor). **SOLID**
- **madaio2020** (CHI '20) — fairness checklists; third of the documentation
  trio; cut candidate if trimming. **CLUSTER**
- **lee2020** (CHI EA '20) — human-centered fair-AI framing; the designated
  exemplar that seeded the citation graph, cited once for "fairness is defined
  relative to a decision context." It is an Extended Abstract carrying a
  framing-level claim; the paper survives its removal, but it is the declared
  seed of the bibliography's provenance — keep, knowingly. **SOLID (venue
  light)**
- **duarte2012** (RFS) — appearance-based trust effects in P2P lending;
  bracket evidence that lending discrimination is documented. **SOLID**
- **pope2011** (JHR) — discrimination on Prosper.com; same bracket, the
  strongest entry in it. **SOLID**
- **bartlett2019** (JFE, published 2022) — fintech-era lending discrimination;
  same bracket; year was corrected to the published article in this branch.
  **SOLID**

## Scoreboard

51 citations: 7 load-bearing, 28 solid, 10 cluster, and 6 carrying a named
weakness (butler2017 fit; sarwal2024 record; corbettdavies2018 and
luo2026b superseded/preprint records; stumpf2024 venue; lee2020
venue-light). If the concision
pass needs to cut citations, the order is: luo2026, deshpande2022, kim2025,
madaio2020, raji2019, metaxa2021 — none is engaged in the text, and no
argument bullet in ARGUMENT_SKELETON.md depends on any of them.
