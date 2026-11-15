---
description: Security scan, report, or fix with the Vyche skill (scan/fix/report)
---

Use the `vyche` skill (ID `vyche`). Load it if it is not already loaded. Follow its process.

User request: $ARGUMENTS

Step 0 of the skill decides the mode from the first word, and the rest is scope. Handle the empty case like this:

- **`$ARGUMENTS` empty** -> **`report`** mode (read-only, most informative). Scope: the files modified in the working tree. If `git status` shows a clean tree, use the source files in the working directory and say that is the rule you used.
- **`$ARGUMENTS` unclear** -> also `report`, and say so on the first line so the user can correct it.

Whatever mode wins, `report` without an explicit request to save is read-only: write nothing, not even a report file. `/vyche scan X` and `/vyche/scan X` must produce the same output - both resolve to the skill's Step 6 scan contract, which is the only definition of the scan format.
