---
description: Vyche report - full read-only security report with evidence and fixes
---

Use the `vyche` skill in **report** mode. Follow its process exactly (Steps 0-5, then the report output contract).

Scope: $ARGUMENTS

Rules for this run:
- Read-only. Do not modify, create, or delete any project file, except writing the report file if explicitly asked.
- State the scope in the first line of your answer.
- Use `references/report-template.md` exactly, including the "Needs human review", "Checked and found no issue", and "Not covered / limits" sections.
- Every finding needs file, line, and a quoted snippet.
- No low-confidence findings in the main list.
- If the scope above is empty, start from the files modified in the working tree plus what they call.
