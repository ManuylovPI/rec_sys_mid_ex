# Report plan — sweet.tv final exam (manuilov)

Deliverables (submitted through the course channel, nothing else):
1. `manuilov_exam_report.pdf` — the report.
2. `manuilov_exam_session.jsonl` — the original, unmodified Claude Code transcript of this session (I copy it myself at the very end).

Binding rules: `docs/exam_quiz_GSB.md` (exam spec) + the course homework guidelines (`docs/homework_guidelines.pdf`).
Style reference: my A05 report (`docs/style_example_a05.pdf`) — same look and tone. Sample report: `docs/sample_report_a01.pdf`.

## Hard constraints
- **≤ 5 pages excluding references.** Dense layout like A05: serif body ~10 pt, tight margins, numbered tables
  "TABLE I. ...", figures "Fig. 1. ...", inline code in red monospace, bold run-in paragraph heads.
- **Every number comes from a saved file in the repo** (experiments.csv, docs/*.md, LOG.md). No number from memory.
- **No fabricated or unchecked references.** Check that every URL/DOI resolves. If a source can't be opened, say so
  and leave it for me to verify; never invent authors, years or venues.
- **No claim of verification that wasn't done.** Things I verify by hand are marked [PAVEL] below; leave a clear
  placeholder for them, don't write them as done.
- No A/B test, online experiment or revenue claim. Qualify "never / always / better" to the evidence.
- English, plain and specific, first person ("I"). Not marketing tone.

## Required elements from the exam spec (checklist — all must be in the PDF)
- [ ] Link to the GitHub repo https://github.com/ManuylovPI/rec_sys_mid_ex and the final commit hash.
- [ ] Direct links to the submission files in the repo, including `submissions/final.csv`, mapped to Kaggle names
      (`submission (N).csv` → repo file). The instructor asked for this explicitly.
- [ ] Screenshot of the Kaggle Submissions page (reports/figures/kaggle_submissions.png) with all ten scores.
- [ ] Designated final submission named explicitly: submission (10).csv = hybrid_v4_cov80, 0.46071 public / 0.44493 private.
      Note that Kaggle disables selection for late submissions, so the report designates it.
- [ ] Join rule (channel + interval overlap), how views were merged per user/channel, the watch threshold and why,
      justified with the observed coverage/duration distribution.
- [ ] Handling of tv_show_id = 0 (never an item; kept only as context). The 10.8% labelling fact.
- [ ] Validation split and why (history 11-20 → target 21-30, temporal check on folds ending before week 21);
      models fit on training data only.
- [ ] Candidate pool (labelled shows airing in the target window), repeats allowed, identical across methods.
- [ ] Cold-start fallback (popularity), identical everywhere, and how many test users needed it.
- [ ] How each method produces exactly five ids.
- [ ] Hyperparameters, seeds, runtimes, environment.
- [ ] No future viewing used; test schedule used only for channel/time; CBF metadata strictly from weeks ≤ 30 (deliberate).
- [ ] Two required methods evaluated individually (ALS = MF, CBF) + popularity baseline + repeat + slot habits.
- [ ] Final strategy = hybrid: components, how the re-ranker/ensemble and its settings were chosen, comparison with each
      component on the same hold-out.
- [ ] Two users (heavy + light), same for all methods, each method's top-5 with id, title, category vs what they watched.
- [ ] The required business question answered: which strategy for sweet.tv and why — familiar vs new, how methods
      differ, where popularity already does well, validation + cost + user experience, limitations starting with 10.8%.
      Association rules and PageRank were not implemented: may be discussed only conceptually, clearly marked as such.
- [ ] External sources disclosed: the prize-winning write-up (idea for the label definition and some features, no code).

## Structure (A05 order)
Title block: paper-style claim title (like A05), then Student: Manuilov Pavel · Team: Individual ·
Email: pimanuylov@edu.hse.ru · Date: 2026-10-24 · Assignment: Final exam — TV program recommendation on sweet.tv.

Abstract (50-150 words, 4 sentences: problem, method, key result with numbers, takeaway) + Index Terms.

1. Introduction — problem, motivation, one concrete example (one real test user: history → predicted top-5),
   contributions (1-2 bullets, no over-claim).

2. Related Work — 3-7 IEEE references actually used. Candidates to check and use only if relevant and verifiable:
   the competition page; the prize-winning write-up (Towards Data Science); Hu, Koren, Volinsky, "Collaborative filtering
   for implicit feedback datasets", ICDM 2008; Ke et al., "LightGBM", NeurIPS 2017; Burges, "From RankNet to LambdaRank to
   LambdaMART: An overview", MSR-TR-2010-82; Cremonesi, Koren, Turrin, RecSys 2010 (popularity as a strong top-N baseline);
   the `implicit` library docs; DuckDB. Plus "Alternatives considered" (association rules, personalized PageRank, LightFM)
   with a one-line rationale each.

3. Method — approach; pipeline as numbered steps (join → interactions → label → candidates → features → LightGBM
   ensemble → top-5); tools with versions; key design decisions (2-3 non-obvious: coverage-based label; recency folds;
   strict reading of the test-schedule rule); configuration (hyperparameters, seeds, environment, runtimes).

4. Experiments — setup; TABLE: all methods on the same hold-out (cov50 main + cov80, temporal check, runtime);
   TABLE: the ten Kaggle submissions (what changed, validation, public, private) + the progression figure;
   comparison vs baseline; Verification bullets: brute-force join check (0 mismatches), MAP@5 unit test,
   validation→leaderboard predictions written before submitting, format checks, [PAVEL] hand-computed AP@5 for one user.
   4.1 Two users and the strategy question (table with each method's top-5 + discussion + decision).

5. Discussion — Failure case: the validation label. n_days fitted three leaderboard points almost perfectly, yet was
   wrong: all three submissions used any-overlap logic, so the fit was self-consistent; prediction for repeat_cont50 vs
   the actual 0.417. Root cause, fix, verification. Second, smaller: the 3-hour timezone shift in day counts (errata).
   What worked (2-3), what surprised me / didn't work (2-3, e.g. ALS and CBF below popularity; slot habits strong alone
   but redundant in the hybrid; recency gains invisible on validation), next improvement (one concrete thing).
   [PAVEL] will rewrite this section in his own voice — write a solid draft he can edit.

6. AI Usage Disclosure — tools with versions: Claude Code (model name and version as the session reports it) — this
   session, start/end time, number of my prompts and tool calls (count them from the transcript file); Claude (claude.ai
   chat, Anthropic) outside Claude Code: planning the stages, drafting my prompts, finding and reading the prize-winning
   write-up, this report plan. How AI was used (categories). What I personally verified [PAVEL — placeholders].
   What I trusted without verification (honest list). Session log reference: manuilov_exam_session.jsonl, the
   unmodified Claude Code transcript.

References — IEEE numbered, with [Accessed: date].

## Hand-check worksheet (for me)
Create `reports/hand_check.md`: one test user from the validation set with the five predicted ids of the final setup and
their cov50 ground-truth list, so I can compute AP@5 by hand and compare it with the value the code prints for that user.
Print that code value in the file. Don't compute the AP by hand for me.

## Build
HTML + CSS → PDF (headless Chrome/Edge or any tool available), source kept in `reports/`. Check the page count and that
every figure renders. Save the PDF as `reports/manuilov_exam_report.pdf`.
