---
description: Vyche fix - analyze, then apply minimal security patches without committing
---

Use the `vyche` skill in **fix** mode. The mode is already decided by this command: **skip Step 0's mode detection entirely, and treat everything in `$ARGUMENTS` as scope, even when it is a bare file path.** Analyze first (Steps 1-5), then patch (Step 6, fix).

Scope: $ARGUMENTS

Rules for this run:
- Analyze before touching anything. Patch only findings that pass the verification gate with High or Medium confidence.
- Smallest change that closes the hole and keeps behavior identical. Follow the project's existing style and libraries.
- Do not refactor unrelated code, do not add dependencies unless truly unavoidable (and say so), do not touch low-confidence items.
- Do not commit, push, or delete files. Leave changes in the working tree for `git diff`.
- Re-read every changed spot afterwards and confirm the hole is closed and nothing new opened.
- Close with the "Changes made" table, a "Not changed" list if needed, and the test command to run.
- **The output is the full report, not just a changes table.** Findings, evidence, and limits all appear, exactly as in `report` mode, with the `Changes made` and `Not changed` sections appended. A run that shows only a table is incomplete even if the patch itself is correct.
- If every finding turns out to be un-patchable, that is a valid result, not a failed run: say how many findings you closed (possibly zero), and for each one name the decision only the user can make. Write `| (none) | - | No files changed | <what you need> |` so the table is present and obviously empty rather than missing.
- If the scope above is empty, start from the files modified in the working tree plus what they call.
