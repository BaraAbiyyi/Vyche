---
description: Vyche fix - analyze, then apply minimal security patches without committing
---

Use the `vyche` skill in **fix** mode. Follow its process exactly: analyze first (Steps 0-5), then patch (Step 6, fix).

Scope: $ARGUMENTS

Rules for this run:
- Analyze before touching anything. Patch only findings that pass the verification gate with High or Medium confidence.
- Smallest change that closes the hole and keeps behavior identical. Follow the project's existing style and libraries.
- Do not refactor unrelated code, do not add dependencies unless truly unavoidable (and say so), do not touch low-confidence items.
- Do not commit, push, or delete files. Leave changes in the working tree for `git diff`.
- Re-read every changed spot afterwards and confirm the hole is closed and nothing new opened.
- Close with the "Changes made" table, a "Not changed" list if needed, and the test command to run.
- If the scope above is empty, start from the files modified in the working tree plus what they call.
