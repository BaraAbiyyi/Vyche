# Contributing to Vyche

Vyche is a pack of instructions, so its quality is the quality of its writing. Contributions are welcome in three shapes: new vulnerability patterns, new fixtures, and corrections.

## Before you write

Open an issue first for anything large: a new language, a new category, a restructure of `SKILL.md`. Small fixes (a wrong API name, a missing CWE, a clearer pair of examples) can go straight to a pull request.

## Ground rules

1. **Write it yourself.** No copied text from other skills, blog posts, or documentation. If a pattern is inspired by an external source, name the source in the pull request. Paraphrase, never paste.
2. **Every pattern needs three things**: the vulnerable code, the fixed code, and the reason it is vulnerable in one sentence. A sink list with no safe counterpart is not useful.
3. **Verify against the official source.** ORM and framework APIs change. Check the current documentation for the version you are writing about, and say which version you checked.
4. **No exploit code.** Conceptual attack paths only. No payloads, no weaponized scripts, no step-by-step attack instructions.
5. **No real secrets.** Fixtures use obviously fake values.
6. **Keep it scannable.** Tables over paragraphs. Short sentences. No filler.

## Adding a vulnerability pattern

1. Put it in the right section of `references/language-patterns.md`, `references/frontend-patterns.md`, or `references/vulnerability-checklist.md`.
2. Add the sink to the sink list, the mitigation to the safe list, and the CWE id.
3. Add or adapt a code pair. Keep it under about 15 lines per block.
4. If the pattern is specific to AI-generated code, it belongs in V-10 as well.

## Adding a fixture

Follow `examples/README.md`:

1. New folder under `examples/`, small (one to five files), self-contained, no network.
2. At least one decoy, so precision is testable.
3. `labels.json` with `expected_main`, `expected_review`, and `decoys`, using an `anchor` substring for each item.
4. Add a row to the fixture map.
5. Run the fixture yourself with each mode and record what happened in the pull request.

## Changing `SKILL.md`

`SKILL.md` is the contract. Keep it under 500 lines, keep the mode rules unambiguous, and keep the quality gate checklist intact. If you add a step, say what it prevents. If you remove one, say what replaces it.

Reference file names are stable and referenced by the PRD: `language-patterns.md`, `frontend-patterns.md`, `vulnerability-checklist.md`, `report-template.md`. Do not rename them without updating `SKILL.md`, the commands, and the PRD together.

## Style

- English for skill content, so the instruction files stay consistent and token-efficient. Agent output follows the user's language, not the file's.
- Code fences always carry a language tag.
- Headings in sentence case.
- Tables for anything with more than two columns.
- No emojis in the skill files.

## Pull request checklist

- [ ] Change is in the right file and section.
- [ ] Vulnerable and fixed examples both present.
- [ ] CWE id included and correct.
- [ ] Checked against official documentation for a named version.
- [ ] No copied text, no exploit code, no real secrets.
- [ ] Fixtures updated or added if behavior changed.
- [ ] `CHANGELOG.md` updated under "Unreleased".
- [ ] If `SKILL.md` changed: still under 500 lines, mode rules still unambiguous.

## Reporting a bug

Include: the agent and version, the model, the command you ran, the scope, what you expected, what you got, and the smallest file that reproduces it. Remove secrets and private code before pasting.

## License of contributions

By contributing you agree that your work is released under the project license (MIT).
