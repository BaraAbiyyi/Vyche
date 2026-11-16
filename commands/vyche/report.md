---
description: Vyche report - full security report with evidence and fixes, saved as vyche-report.md
---

Use the `vyche` skill in **report** mode. The mode is already decided by this command: **skip Step 0's mode detection entirely, and treat the `Scope:` line below as the scope, even when it is a bare file path.** Then follow Steps 1-5 and the report output contract in Step 6.

Scope: $ARGUMENTS

Rules for this run:
- Write the report to `vyche-report.md` in the project root and say where it went. That is the only file this run writes; do not modify, create, or delete any source or config file.
- Overwrite an existing `vyche-report.md`; do not create `vyche-report-2.md` or a timestamped variant.
- If the user explicitly asks to keep the report in the conversation only, skip the file and say so.
- State the scope in the first line of your answer.
- Use `references/report-template.md` exactly, including the "Needs human review", "Checked and found no issue", and "Not covered / limits" sections.
- Every finding needs file, line, and a quoted snippet.
- No low-confidence findings in the main list.
- If the scope above is empty, start from the files modified in the working tree plus what they call. If the working tree is clean, use the source files in the working directory and say that is the rule you used.
