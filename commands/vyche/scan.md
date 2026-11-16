---
description: Vyche scan - fast read-only security scan with a findings table
---

Use the `vyche` skill in **scan** mode. The mode is already decided by this command: **skip Step 0's mode detection entirely, and treat the `Scope:` line below as the scope, even when it is a bare file path.** Then follow Steps 1-5 and the scan output contract in Step 6.

Scope: $ARGUMENTS

Rules for this run:
- Read-only. Do not modify, create, or delete any project file.
- State the scope in the first line of your answer.
- Cap the table at the 10 most severe findings.
- No low-confidence findings in the main list.
- If the scope above is empty, start from the files modified in the working tree (`git status`, `git diff`) plus what they call. If the working tree is clean, use the source files in the working directory and say that is the rule you used.
