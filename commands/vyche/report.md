---
description: Vyche report - full read-only security report with evidence and fixes
---

Use the `vyche` skill in **report** mode. The mode is already decided by this command: **skip Step 0's mode detection entirely, and treat everything in `$ARGUMENTS` as scope, even when it is a bare file path.** Then follow Steps 1-5 and the report output contract in Step 6.

Scope: $ARGUMENTS

Rules for this run:
- Read-only. Do not modify, create, or delete any project file, except writing the report file if explicitly asked.
- State the scope in the first line of your answer.
- Use `references/report-template.md` exactly, including the "Needs human review", "Checked and found no issue", and "Not covered / limits" sections.
- Every finding needs file, line, and a quoted snippet.
- No low-confidence findings in the main list.
- If the scope above is empty, start from the files modified in the working tree plus what they call. If the working tree is clean, use the source files in the working directory and say that is the rule you used.
