# Vyche

A security gate for code, especially code written with AI.

Vyche is an **agent skill**: a pack of Markdown instructions your coding agent reads. No install script, no dependencies, no network calls, no hidden binaries. It finds vulnerabilities by reasoning about your code, proves every finding with evidence, and can patch the confirmed ones.

Built and tested with [OpenCode](https://opencode.ai). Other agents that read Markdown skills should work on a best-effort basis.

## Why

AI writes the happy path. It usually does not add the ownership check, the bound parameter, the `HttpOnly` flag, or the environment variable for the secret, because nobody asked for them. The code runs, the demo works, and the vulnerability ships.

Vyche exists to catch that, before production, without a scanner to install or a report nobody can act on.

## Install (OpenCode)

```sh
git clone https://github.com/BaraAbiyyi/Vyche.git vyche
cd your-project

# skill: SKILL.md + references/
mkdir -p .opencode/skills/vyche
cp -r ../vyche/SKILL.md ../vyche/references .opencode/skills/vyche/

# commands: /vyche, /vyche/scan, /vyche/fix, /vyche/report
mkdir -p .opencode/commands/vyche
cp ../vyche/commands/vyche.md .opencode/commands/
cp ../vyche/commands/vyche/*.md .opencode/commands/vyche/
```

The trailing `vyche` in the clone command is load-bearing. Without it the repo lands in `Vyche/`, and every `../vyche/` path below breaks on a case-sensitive filesystem.

Windows (PowerShell):

```powershell
git clone https://github.com/BaraAbiyyi/Vyche.git vyche
Set-Location your-project
New-Item -ItemType Directory -Force .opencode/skills/vyche, .opencode/commands/vyche | Out-Null
Copy-Item ../vyche/SKILL.md, ../vyche/references -Destination .opencode/skills/vyche -Recurse
Copy-Item ../vyche/commands/vyche.md -Destination .opencode/commands/
Copy-Item ../vyche/commands/vyche/*.md -Destination .opencode/commands/vyche/
```

OpenCode picks the files up without a restart. Paths and options differ between OpenCode versions; if `/vyche` does not appear, check the skills and commands docs for your version.

To install once for every project instead, copy the same files to `~/.config/opencode/skills/vyche/` and `~/.config/opencode/commands/` (on Windows, `%USERPROFILE%\.config\opencode\...`). The skill ID comes from the directory name, so keep it `vyche`. Project-local files override global ones.

## Use

| Command | Changes files | Output |
| --- | --- | --- |
| `/vyche scan <scope>` | No | Table of findings: severity, CWE, location, one-line reason |
| `/vyche report <scope>` | Creates `vyche-report.md` in the project root, nothing else | Full report: evidence, why it matters, recommended fix, limits |
| `/vyche fix <scope>` | Yes, minimal patches, no commit | Full report plus a changes table, what still needs you, test command |

`/vyche/scan`, `/vyche/report`, and `/vyche/fix` do the same thing with the mode as part of the command.

```sh
/vyche scan folder src/auth
/vyche report entire project before release
/vyche fix the SQL injection in app/db.py
/vyche fix finding 2
/vyche is this login flow safe?
```

Scope is free text. If you do not name one, Vyche starts from the files modified in your working tree; if the tree is clean, it uses the source files in the working directory. Either way it tells you which rule it picked.

Default mode is `report`: it reads the code and writes only `vyche-report.md`, nothing else. `scan` is the zero-write option.

## How it works

1. **Mode and scope** are parsed from your sentence, then stated back in one line.
2. **The project is mapped** first: stack, entry points, sensitive assets, trust boundaries.
3. **Only the matching reference sections load**, so a Python project never pays for the Rust page.
4. **Data is traced from source to sink** instead of pattern-matched, and controls that have no data flow (authorization, secrets, configuration) are checked separately.
5. **Every candidate passes a five-part gate**: evidence, reachability, mitigation check, confidence, context-aware severity. Low confidence goes to a "Needs human review" section, never the main list.
6. **Output** follows the mode: a table, a report, or a patch left in your working tree for `git diff`.

That process is aimed at the two ways LLM reviews fail: inventing vulnerabilities, and skimming long files so the real ones are missed.

## What it checks

V-1 Injection · V-2 Access control · V-3 Authentication and sessions · V-4 Cryptography and secrets · V-5 Sensitive data exposure · V-6 Input and file handling · V-7 Requests, redirects, CORS · V-8 Configuration · V-9 Dependencies and supply chain · **V-10 AI-generated code patterns** · V-11 Logic and concurrency · V-12 Memory safety

V-10 is the reason Vyche exists: placeholder secrets that ship, validation omitted because the prompt described the happy path, insecure defaults, outdated tutorial patterns, security TODOs left behind, and comments claiming code is safe.

## Languages and frameworks

| Backend | Frontend |
| --- | --- |
| JavaScript / TypeScript (Node, Express, NestJS) | React |
| Python (Django, Flask, FastAPI) | Next.js (Server Actions, middleware, hydration) |
| Go | Vue / Nuxt |
| Rust | Svelte / SvelteKit |
| Java / Spring (JPA, Hibernate) | Browser specifics (cookies, storage, postMessage, CSP) |
| Ruby / Rails (ActiveRecord) | |
| PHP / Laravel (Eloquent) | |

SQL injection reference per ORM: Prisma, Sequelize, TypeORM, SQLAlchemy, Django ORM, GORM, Hibernate/JPA, ActiveRecord, Eloquent, sqlx, Diesel.

## Fixtures

`examples/` contains seven hand-labelled mini-projects (`python-sqli`, `python-clean`, `full-app`, `hardcoded-secret`, `prompt-injection`, `ambiguous-auth`, `nextjs-action`). Each has a `labels.json` with the findings a correct run must produce, plus decoys that must not be reported. They exist so results can be scored (precision, recall, F1) instead of judged by impression. See `examples/README.md`.

## Limits

Vyche reads code. It does not run it, and there is no scanner behind it.

- Findings are not exhaustive. Complex business logic, framework magic, and runtime configuration can hide issues that reading alone will not surface.
- Long files and large repositories can be partially covered. Vyche states what it skipped.
- No findings does not mean safe. It means nothing was found in the reviewed scope.
- Have a human review authentication, payments, cryptography, and access control before production.

Vyche also does not write exploits, does not attack systems, and does not send your code anywhere outside the current agent session.

## Project structure

```
vyche/
├── SKILL.md                      # workflow, mode contract, quality gate
├── references/
│   ├── language-patterns.md      # 7 languages + SQL injection by ORM
│   ├── frontend-patterns.md      # React, Next.js, Vue, Svelte, browser
│   ├── vulnerability-checklist.md# V-1..V-12 with CWE ids
│   └── report-template.md        # scan/report/fix output contracts
├── commands/                     # copy into .opencode/commands/
├── examples/                     # labelled fixtures for evaluation
├── docs/                         # PRD and release checklist
├── CONTRIBUTING.md
├── CHANGELOG.md
└── LICENSE
```

## Contributing

New patterns, new fixtures, and corrections are welcome. Read `CONTRIBUTING.md` first: every pattern needs a vulnerable example, a fixed example, and a source.

## License

MIT. See `LICENSE`.
