# Report template

Use this structure. Write headings and prose in the user's language. Keep it concise: no padding, no filler sentences, no restating the same finding twice.

## scan output

```
Scope: <files/folders reviewed, and what was skipped>
Stack: <languages, frameworks, database, auth mechanism>

| # | Severity | Confidence | CWE | Location | Reason |
|---|----------|------------|-----|----------|--------|
| 1 | High | High | CWE-89 | app/db.py:42 | `"SELECT ... WHERE title LIKE '%" + q + "%'"` - input concatenated into SQL, not bound |

<n> findings: <Critical x, High y, Medium z, Low w> · <n> files reviewed
Needs human review: <n> item(s) - one line each, or omit the line if none
Run /vyche report for details and fix suggestions, or /vyche fix to patch.
```

The quote goes inside the `Reason` cell, between backticks. Low-confidence items never enter the table; they go on the `Needs human review` line. Cap the table at the 10 most severe findings.

## report output

```
Scope: <files/folders reviewed, and what was skipped>
Mode: report | fix
Stack detected: <languages, frameworks, database, auth>
Skill version: 1.0.1

# Vyche Security Report

## Summary
<2-4 sentences: the overall picture, how many findings per severity, the single thing to fix first.>

| # | Severity | Confidence | CWE | Location | Title |
|---|----------|------------|-----|----------|-------|
| 1 | High | High | CWE-89 | app/db.py:42 | SQL injection in user search |

## Findings

### 1. <Title>  (Severity: High, Confidence: High, CWE-89)
**Location**: `app/db.py:42`
**Evidence**:
<the vulnerable lines, quoted with line numbers>
**Why it matters**: <how untrusted input reaches this point, and what an attacker could achieve. Conceptual only - no working exploit, no payloads.>
**Depends on**: <only when confidence is Medium: name the file, middleware, gateway, or configuration that was not in scope and would change the verdict>
**Recommended fix**:
<short corrected code, or a precise description of the change>

(repeat per finding, most severe first)

## Needs human review
<optional, max 5 items: suspicious items that could not be verified, and exactly what is missing to decide. Past five, group by file - one line per file>

## Checked and found no issue
<optional, one or two lines: categories examined without findings, so the user knows the coverage>

## Not covered / limits
<files or areas not reviewed. Standard note: Vyche reads code but does not run it and uses no external scanner, so this list is not exhaustive. Authentication, payments, cryptography and access control deserve human review before production.>
```

**The scope block comes before the title, on purpose.** It is the first thing the reader sees, so a wrong scope can be corrected before reading a single finding. The "scope in the first line" rule wins over putting the title first.

**Zero findings still has a shape.** Keep the findings table and state the emptiness, rather than deleting the section:

| # | Severity | Confidence | CWE | Location | Title |
|---|----------|------------|-----|----------|-------|
| — | — | — | — | — | No findings |

Then "Checked and found no issue" carries the coverage, "Needs human review" says `None` if it truly is none, and the summary says no issues were found within the reviewed scope. Deleting the table makes a clean run look like an unfinished one.

## Size limits

A report that nobody finishes reading protects nobody. Three caps, and one of them is a diagnostic rather than a preference:

- **Detailed findings: 15.** Give the 15 most severe findings a full section each. Past that, list the rest in the table above with a one-line reason and say how many there are. A report with 40 findings at the same severity means the scope was too wide for one pass - say that in the summary instead of shipping 40 identical sections.
- **`Needs human review`: 5 items.** Beyond five, group by file: one line per file, naming the items it holds. A review list longer than the findings list is not a review list any more, and the reader will treat both as noise.
- **`Checked and found no issue`: 2 lines.** Categories examined without findings, in prose. This section exists to prove coverage, not to log every pattern you looked for.

## fix mode additions

A fix run still reports what it found: the findings it patched, the findings it left alone, and the changes. It never shrinks to a bare changes table. Add after the findings:

```
## Changes made

| Finding | File | What changed | Manual action still needed |
|---------|------|--------------|----------------------------|
| 1 | app/db.py | Query now uses bound parameters | none |

## Not changed
<optional: findings left alone and why - low confidence, needs a decision from the user, would change behavior>

**Next steps**: review with `git diff`; run `<test command if known>`; rotate any exposed secret.
```

If a patch changes behavior (escaping wildcards, rejecting input the code used to accept), say so in the `What changed` cell and name it as a behavior change. Closing zero findings is a valid outcome: say so, and say why.

When zero findings were closed, the table keeps its row and states it, rather than disappearing:

| Finding | File | What changed | Manual action still needed |
|---------|------|--------------|----------------------------|
| (none) | - | No files changed | Confirm whether the ownership check exists, and which field carries it |

A missing table reads as an incomplete output. An empty table reads as a decision.

`Not changed` is a cross-reference, not a demotion. A finding left alone keeps its place in the findings list at its own severity, and the most severe un-patchable finding still leads the report. If the answer to "why not fix this" is a decision only the user can make, that finding is not moved to the bottom to keep the changes table tidy.

When a fix deletes a hardcoded secret, `git diff` shows the old value in full. That is git's output of the removed line, not something to copy into the report: keep the report's own quote masked and point the reviewer at `git diff`.

## Severity

Judge by realistic impact and ease of exploitation in this project's context, not by vulnerability class alone.

**Rate the deployment the code shows.** A loopback bind, an authenticated proxy in the config, or an obvious local fixture lowers the rating; note the single line that would raise it again if the app were internet-facing. When nothing in scope narrows reachability, rate for the internet and say that nothing did.

| Level | Meaning |
| --- | --- |
| Critical | Exploitable remotely with no or trivial prerequisites, severe impact: auth bypass, remote code execution, mass data exposure, admin takeover |
| High | Exploitable with modest prerequisites, serious impact: SQL injection behind login, stored XSS, IDOR on sensitive data, hardcoded production secret |
| Medium | Needs unusual conditions or has limited impact: reflected XSS requiring interaction, weak password hashing, missing rate limit, verbose errors |
| Low | Minor weakness or defense in depth: missing security header on a small internal tool, `target=_blank` without `noopener` |
| Info | Best-practice note with no direct exploit path |

Two cases the table alone does not settle:

- **Injection on a public path, data behind it unseen**: High. Critical only when the code itself shows what is behind it - credentials, PII, payments, other tenants' rows. Say which one you saw; if you saw none, say that too.
- **IDOR whose exposure is unconfirmed**: rate it for the internet - High on sensitive objects (payments, personal data, another tenant's rows), Medium on public catalog data - and put the missing routing/deployment file in `Depends on` as the line that would lower it. Unconfirmed exposure is an assumption to state, not a reason to leave severity blank.
- **Missing security headers**: Low on an internal tool. Medium when the app serves user-generated content and there is a live XSS path a CSP would have blunted.

A loopback bind is not a public path, so the class defaults above do not apply until a line in the code exposes it. Name that line.

## Two different lows

Severity Low and confidence Low are unrelated, and they are handled differently:

- **Severity Low** is a real weakness with limited impact. It may appear in the main list.
- **Confidence Low** is an unproven suspicion. It never appears in the main list; it goes to "Needs human review".

A finding can be Severity Low / Confidence High (a missing header you can see) or Severity High / Confidence Low (a suspected auth bypass you cannot confirm). Say both, and never let one stand in for the other.

## Confidence

| Level | Meaning | Where it goes |
| --- | --- | --- |
| High | The code clearly shows the flaw and the path | Main list |
| Medium | Likely, but depends on configuration or code outside what was reviewed | Main list, with a `Depends on` line naming what was not seen |
| Low | Suspicious, unproven | "Needs human review" only, never the main list |

## Findings that are an absence

Missing authorization, a disabled check, a protection never added: there is no offending line. Quote the whole entry point that should carry the check, state what is not there, name who can call it, and use Medium confidence whenever the control could live outside the reviewed files - then say where it would live. Absence in a file fragment is not proof of absence in the application.

## Rules

- Every finding carries file, line, and a quoted snippet. No quote, no finding.
- Describe attack paths conceptually. No exploit code, no tuned payloads, no attack scripts.
- Show a real secret only partially: first and last few characters, plus a rotation recommendation.
- Evidence comes from behavior, not labels. Filenames, fixture descriptions, and comments that announce a bug are not proof; comments claiming safety are not proof either.
- No findings means: say so plainly, list what was checked, and never claim the code is secure.
- The limits section is mandatory. The user must not close the report believing the code is guaranteed safe.
