---
description: Vyche scan - fast read-only security scan with a findings table
---

Use the `vyche` skill in **scan** mode. Follow its process exactly (Steps 0-5, then the scan output contract).

Scope: $ARGUMENTS

Rules for this run:
- Read-only. Do not modify, create, or delete any project file.
- State the scope in the first line of your answer.
- Cap the table at the 10 most severe findings.
- No low-confidence findings in the main list.
- If the scope above is empty, start from the files modified in the working tree (`git status`, `git diff`) plus what they call.
