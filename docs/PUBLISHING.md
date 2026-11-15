# Publishing checklist

Run this before making the repository public. The skill is harmless to ship; the working directory it was built in is not.

## 1. Remove files that are not part of the product

| File / folder | Why it must not ship |
| --- | --- |
| `AGENTS.md` | Personal instructions for the developer's own agent environment. It would be read as project instructions by anyone who clones the repo, and it exposes internal working notes. |
| `docs/PRD Vyche Agent Skill untuk Analisis, Perbaikan, dan Pelaporan Keamanan Kode.md` | Superseded v0.1 draft. Either delete it or move it under `docs/archive/` with a note. Decide one; do not ship two PRDs. |
| `node_modules/`, `vendor/`, `dist/`, `.venv/` | Build artifacts. There should be none, since the project has no build step. |
| Local config: `opencode.json`, `.env`, `.vscode/`, editor leftovers | Environment-specific. |

Command to remove the personal file once you are sure:

```powershell
Remove-Item .\AGENTS.md
```

## 2. Verify the shipped tree

```powershell
Get-ChildItem -Recurse -File | Where-Object { $_.FullName -notmatch '\\\.git\\' } |
  Select-Object FullName, Length | Format-Table -AutoSize
```

Expected top level: `SKILL.md`, `README.md`, `CONTRIBUTING.md`, `CHANGELOG.md`, `LICENSE`, `references/`, `commands/`, `examples/`, `docs/`.

## 3. Check for leaks

```powershell
# real secrets pasted into fixtures or docs
Select-String -Recurse -Pattern 'sk-[A-Za-z0-9]{20,}','AKIA[0-9A-Z]{16}','ghp_[A-Za-z0-9]{30,}','-----BEGIN .*PRIVATE KEY-----'

# personal paths and names
Select-String -Recurse -Pattern 'D:\\vyche','C:\\Users\\','ADVAN'
```

Fixtures use obviously fake values (`vyche-demo-jwt-secret-2024`, `dev-secret-key-change-me`, `security-team@example.com`). That is intended and safe.

## 4. Fill in the placeholders

Already filled for the release (`Bara Abiyyi`, `BaraAbiyyi`). If you fork this and publish under another name, update these:

- `LICENSE`: the copyright holder.
- `README.md`: the clone URL, in both the shell and PowerShell blocks.
- `docs/PRD.md`: the `Pemilik` field in the document header.
- `docs/PUBLISHING.md`: the remote URL in §6.

## 5. Verify the skill actually loads

1. In a clean test project, follow the install steps in `README.md`.
2. Run `/vyche scan examples/python-sqli` from the Vyche repo (or copy the fixture into the test project).
3. Confirm the output is a findings table with `CWE-89`, the correct file, and a quoted snippet.
4. Run `/vyche scan examples/python-clean` and confirm zero findings, with a list of what was checked and no claim that the code is secure.
5. Run `/vyche report examples/full-app` and confirm all six template sections are present.
6. Run `/vyche fix examples/python-sqli`, then `git diff` and confirm the change is minimal and uncommitted.
7. Confirm `git status` is clean after the two read-only runs.

A run that passes all seven is a release candidate.

## 6. Release

```powershell
git init
git add .
git commit -m "vyche 1.0.1"
git branch -M main
git remote add origin https://github.com/BaraAbiyyi/Vyche.git
git push -u origin main
git tag -a v1.0.1 -m "vyche 1.0.1"
git push origin v1.0.1
```

Then on GitHub:

- Description: `Security review and remediation skill for AI coding agents. Read-only scan and report, minimal fix. Works with OpenCode.`
- Topics: `security`, `agent-skill`, `opencode`, `code-review`, `sast`, `llm`.
- License: MIT.
- Enable Issues.

## 7. After publishing

- Record the release commit hash in the evaluation log, so every test run can be traced to an exact version of the skill.
- Any change to `SKILL.md` or `references/` after a release requires a version bump before further evaluation runs, or the comparison is invalid. Current release: `v1.0.1`.
