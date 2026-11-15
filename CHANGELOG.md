# Changelog

All notable changes to this project. Format based on Keep a Changelog, versioning follows SemVer.

## [Unreleased]

### Fixed
- The explicit-mode commands (`scan`, `report`, `fix`) no longer re-derive the mode from the first word. They skip Step 0's mode detection and treat all of `$ARGUMENTS` as scope, so `/vyche/scan shop/app.py` can no longer resolve to `report` because `shop/app.py` is not the word "scan". Step references corrected to the output contract in Step 6.
- Router `/vyche` now has a clean-tree branch: an empty `$ARGUMENTS` in a clean repository falls back to the source files in the working directory and says so, instead of prescribing "the files currently modified" when none are. It also restates that the empty case is read-only unless a report file is requested.
- `fix` mode now separates the two axes: confidence is the gate for patching, severity is only the ordering. A Severity Low / Confidence High item is patchable; a Severity High / Confidence Low item is not. Previously "patch High and Medium confidence, most severe first" read as authorizing low-severity patches and invited over-patching.
- A finding left unchanged now keeps its position in the findings list at its own severity. `Not changed` is a cross-reference, not a demotion, so the most severe un-patchable finding still leads the report.
- "Confirm the hole is closed" is now defined as a code re-read, since the mode contract forbids running project code. The skill no longer implies a runtime test it is not allowed to perform.
- A fix that deletes a hardcoded secret no longer collides with secret masking: `git diff` necessarily prints the removed value, so the report keeps its own quote masked, does not paste the diff, and points the reviewer at `git diff`.
- Moving a secret to an environment variable now states what to do about `.env.example` and `.gitignore`, and forbids writing the real value to a new file.
- IDOR with unconfirmed exposure now has a severity rule instead of two rules pulling apart: rate for the internet by data class, put the missing routing file in `Depends on`.
- "Follow the pointer" now separates "absent because the project is an excerpt" from "absent because the control was deleted". Both stay Medium; the skill asks for the reading the evidence supports and what would settle it.
- Listing a git-tracked `labels.json` is explicitly not reading it. Exclusion requires knowing the file exists; opening it is what is forbidden.
- "Plus what they call" is bounded to direct imports, requires, and config that change the modified code, one hop, naming how many application files were actually opened.
- A loopback bind is stated to be not a public path, so the class-based severity defaults do not apply until a line in the code exposes it.
- Zero-finding reports now have a shape: keep the findings table and state the emptiness instead of deleting the section.
- The read-only quality-gate item now asks for a `git status --porcelain` before/after check rather than an unchecked assertion.

## [1.0.0] - 2026-11-15

First complete release. Published at https://github.com/BaraAbiyyi/Vyche, release commit `783211c5583ae51e70cb7f3a3d80297e682e22de` (tag `v1.0.0`). Every evaluation run should be tied to that hash or a later one.

### Added
- `SKILL.md` with the full workflow: mode parsing, scope selection, project mapping, progressive reference loading, source-to-sink tracing, the five-part verification gate, and a pre-output quality gate.
- Three modes with an explicit contract: `scan` and `report` are read-only, `fix` writes minimal patches and never commits.
- `references/language-patterns.md`: JavaScript/TypeScript, Python, Go, Rust, Java/Spring, Ruby on Rails, PHP/Laravel, each with sinks, safe alternatives, framework traps, and vulnerable-to-fixed code pairs.
- SQL injection reference per ORM: Prisma, Sequelize, TypeORM, SQLAlchemy, Django ORM, GORM, Hibernate/JPA, ActiveRecord, Eloquent, sqlx, Diesel.
- `references/frontend-patterns.md`: React, Next.js (Server Actions, middleware, client/server boundary, hydration), Vue/Nuxt, Svelte/SvelteKit, browser specifics.
- `references/vulnerability-checklist.md` restructured into categories V-1 to V-12 with CWE ids, including V-10 for AI-generated code patterns and prompt injection hidden in source.
- `references/report-template.md` with output contracts for all three modes, severity and confidence guides.
- Commands: `/vyche` (router), `/vyche/scan`, `/vyche/report`, `/vyche/fix`.
- `examples/` with seven hand-labelled fixtures and `labels.json` for scoring precision, recall, and F1.
- `README.md`, `CONTRIBUTING.md`, `LICENSE` (MIT), `docs/PRD.md`, `docs/PUBLISHING.md`.

### Changed
- `references/languages.md` replaced by `language-patterns.md` and `frontend-patterns.md`. Scope narrowed to the languages in the PRD; C#, Kotlin, and C/C++ are no longer part of v1.
- `agent-command/vyche.md` replaced by `commands/vyche.md` plus `commands/vyche/*.md`.
- `scan` mode added. Previously the skill had report and fix only.

### Fixed
- Read-only guarantee is now stated as a contract with a table, not an assumption.
- Evidence gate now covers findings that are an absence (missing authorization, disabled protection): quote the whole entry point, state what is not there, and use Medium confidence when the control could live outside the reviewed files.
- Scan output now says where the evidence goes (`Reason` column) and where low-confidence items go (`Needs human review` line), instead of contradicting the quality gate.
- Medium-confidence findings now carry an explicit `Depends on` line naming what was not in scope.
- Fix mode now states that it still reports findings, that it can legitimately close zero findings, and that a patch which changes behavior must be labelled as such.
- Severity is now reproducible across reviewers: rate the deployment the code shows, and state the line that would change the rating.
- Fixtures no longer announce their own answers in the first line. Filenames, fixture descriptions, and comments are not evidence.
- Non-git scopes are handled: fall back to the files given or in the working directory, and say which rule was used.
- Evaluation labels gained `acceptable_extra` (real findings outside the label set) and `acceptable_severity` (severity agreement is scored as a secondary metric).
- Report scope block now sits above the title, resolving the conflict between "scope in the first line" and the template's opening heading.
- Severity guidance added for two cases the table did not settle: injection on a public path with unseen data (High, Critical only when the code shows what is behind it), and missing security headers (Low on an internal tool, Medium when a live XSS path would have been blunted by a CSP).
- Severity Low and confidence Low are now stated as unrelated: Severity Low may appear in the main list, confidence Low never does.
- Non-runtime files (`labels.json`, golden files, snapshot fixtures) are now explicitly excluded from scope, so expected-answer data cannot leak into a review.
- Quality gate now checks the absence-finding exception, the `Depends on` line, and the Low/Low distinction.
- Label schema gained `acceptable_cwe` for classes where two CWE ids are equally defensible (`DEBUG = True` as CWE-1188, CWE-489, or CWE-16).
- **Follow the pointer**: when code or a comment names where a control lives, the skill now reads that file if it is part of the project, instead of treating the claim as an unverifiable dependency. Three verdicts are spelled out: control real (drop the finding), control exists but does not cover this path (finding stands at High), named file absent (finding stands, and the dangling claim is stated as absent rather than as a mitigation).
- Absence findings are now explicitly routed to the main list at confidence Medium with a `Depends on` line, not to "Needs human review". Burying a proven missing check in the review section was hiding the most dangerous class the skill covers.
- Partial-project scope now has a rule: anything whose verdict turns on a file that was not read is confidence Medium, and the unseen files are named in the limits section.
- A confirmed sink with an unread source now has a stated home: main list, confidence Medium, `Depends on` naming the module. Previously it could be demoted to review or inflated to High depending on the reviewer.
- Chained findings are rated separately on their own impact, with the link described in prose. No invented combined severity.
- Non-security defects noticed in passing stay out of the findings list; they go in limits or nowhere.
- Comments claiming safety are no longer ambiguous: they are claims to test, quoted inside the finding they misrepresent, not separate findings. Only reviewer-directed instructions become CWE-1427 items.
- Severity precedence is stated: the table is the internet-facing default, the deployment rating is what ships, and a disagreement names the line that caused it. A hardcoded secret in a loopback-only service is Medium with the escalation line quoted.
- Secrets are now redacted in place inside a quoted evidence line, which reconciles "no quote, no finding" with "never print a full secret".
- `references/vulnerability-checklist.md` gained CWE-306 (no authentication at all - a login endpoint that verifies nothing), which the previous CWE list could not express.
- Dependency checks now handle an absent manifest: say the manifest was not present, route the audit command to Needs human review, and do not claim the category is clean.
- Step 3 gained a minimal reference-loading table, so a Next.js-only scope no longer forces every section open.
- Fixture labels corrected where they punished behaviour the skill prescribes: `ambiguous-auth` now expects a main-list finding at Medium, `python-clean` and `hardcoded-secret` accept the legitimate extras those fixtures actually contain, and `nextjs-action` accepts CWE-862, CWE-639, or CWE-306 for the same Server Action gap.
- Scoring rules gained a placement rule: an absence finding in the main list versus in review is a recorded difference, not a false positive. Confidence agreement is recorded via `acceptable_confidence` and never scored as detection.
- **The evidence boundary** is now a defined term: confidence High requires that the edge of your evidence is the edge of the control's likely home. A subfolder is an excerpt regardless of what the user calls it, which resolves the ambiguity in "High if the whole project was in scope" and makes the absence rule and the partial-scope rule the same rule.
- The CWE-1427 boundary is now an explicit test: a comment asserting a fact about the system is tested and quoted inside the finding it misrepresents; only a comment addressed to the reviewer as an instruction becomes its own finding. Reporting both double-counts one flaw.
- An absent manifest now gets one line in the limits section, promoted to `Needs human review` only when the code's safety actually turns on a dependency version. The previous wording mandated an audit command for every 13-line excerpt, which was the boilerplate the quality gate forbids.
- Report and scan output now have size limits: 15 detailed findings, 5 review items, 2 lines of coverage. Hitting a ceiling is reported as a statement about the scope.
- A view whose routing file is absent is no longer silently downgraded: the missing URL config goes in `Depends on` and the finding stands. Absence of a routing file is not proof the route is unmounted.

## [0.1.0] - 2026-11-15

### Added
- Initial draft PRD.
- Prototype `SKILL.md` with report and fix modes, `references/languages.md`, `references/vulnerability-checklist.md`, `references/report-template.md`, `agent-command/vyche.md`.
