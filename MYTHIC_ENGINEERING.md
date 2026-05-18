# MYTHIC_ENGINEERING.md — Skry

> *How to work in this repository under the [Mythic Engineering](https://github.com/hrabanazviking/Mythic-Engineering)
> convention.*

---

## The Scrolls

| Scroll | What it tells you |
|---|---|
| [`SYSTEM_VISION.md`](SYSTEM_VISION.md) | The soul — what Skry exists to do |
| [`PHILOSOPHY.md`](PHILOSOPHY.md) | The deeper why — the wound it salves |
| [`DOMAIN_MAP.md`](DOMAIN_MAP.md) | Realm boundaries — what belongs where |
| [`ARCHITECTURE.md`](ARCHITECTURE.md) | Bones — the one function and its helpers |
| [`DATA_FLOW.md`](DATA_FLOW.md) | The single river of a skry |
| [`PROJECT_LAWS.md`](PROJECT_LAWS.md) | Immutable rules |
| [`INTERFACE.md`](INTERFACE.md) | Public Python API contract |
| [`README.md`](README.md) | Outward-facing intro |
| [`DEVLOG.md`](DEVLOG.md) | What changed, why, what was learned |
| [`skry/README_AI.md`](skry/README_AI.md) | Notes for editing the code in `skry/` |
| [`docs/bugs/`](docs/bugs/) | Open bug notes from Auditor passes |

## How to Start a Session

1. Read [`DEVLOG.md`](DEVLOG.md) — newest first.
2. Read [`SYSTEM_VISION.md`](SYSTEM_VISION.md) and [`PHILOSOPHY.md`](PHILOSOPHY.md) — both short.
3. Scan [`docs/bugs/`](docs/bugs/) for open notes.
4. State your role.

## How to End a Session

1. Append to [`DEVLOG.md`](DEVLOG.md).
2. Run the Prophecy Rite.
3. Rite of Preservation.
4. Update drifted scrolls.

---

## The Six Roles

| Role | Owns |
|---|---|
| **Skald** | Naming, framing → `PHILOSOPHY.md`, `SYSTEM_VISION.md` |
| **Cartographer** | Maps → `DATA_FLOW.md`, `DOMAIN_MAP.md` |
| **Architect** | Boundaries, interface → `ARCHITECTURE.md`, `INTERFACE.md` |
| **Forge Worker** | Code → `skry/core.py`, `skry/cli.py` |
| **Auditor** (Sólrún Hvítmynd) | Bug hunting → `docs/bugs/` |
| **Scribe** | Documentation → `DEVLOG.md`, README updates |

---

## The Iron Laws

Applied specifically to Skry:

1. **Document before code.** Markdown first.
2. **No pseudocode.** Markdown describes future behavior.
3. **Never delete without asking.**
4. **Full files only** when proposing edits in markdown.
5. **Additive bug fixing.** Never remove structure to fix.
6. **No `print()` in library code.** CLI Rich renderers are fine.
7. **No absolute paths.** Use `pathlib`.
8. **No hardcoded config.** All knobs in `.env`.
9. **Type hints on all public signatures.**
10. **Methods under 50 lines.**
11. **No precomputation.** Ever. (Skry's defining law.)
12. **No storage.** Skry writes nothing.
13. **No generative LLM calls.** Embedding only.
14. **Read-only against the parent corpus.** No `INSERT`, `UPDATE`, `DELETE`, or schema-modifying SQL.

---

## The Bug Hunt Rite

When you find something wrong:

1. **Create a Bug Note** in `docs/bugs/NNNN-slug.md`:
   ```markdown
   # Bug: <name>

   **Discovered:** YYYY-MM-DD by <role>

   ## Symptom
   ## Expected
   ## Suspected domains
   ## Invariant violated
   ## Reproduction
   ## Hypothesis
   ## Fix plan
   ```
2. **Invoke the Auditor.** What invariant failed? Domain? Local or
   structural? What changed near this boundary? Hidden coupling?
3. **Additive fix.** Never remove to fix.
4. **Verify against invariants.**
5. **Update the Bug Note.** `STATUS: resolved`. Do not delete.

---

## The Robustness Rite

For a library this small, the checklist is short:

- Library code: no `print()`; raise on connection failures so caller can
  handle.
- CLI code: Rich for output; `typer.Exit(1)` on user-facing errors.
- Type hints on every function signature.
- `_PROPER_RX` regex tested against unicode, accented letters, multi-word
  proper nouns.
- `_STOP_SURFACE` covers common false positives (days of week, months,
  pronouns).
- Read-only SQL: every query must be a `SELECT`. No exceptions.
- `_known_vocab` returns `None` if `skein_entities` is absent — both code
  paths exercised.

---

## The Prophecy Rite (Testing)

Five layers — start at the **invariant** layer:

1. **Invariant** — `tests/test_invariants.py`:
   - Skry never writes (no `INSERT`/`UPDATE`/`DELETE` SQL in `skry.core`)
   - Every returned entity has at least one `chunks` evidence
   - `vocab_mode` is always exactly `"skein"` or `"open"`
2. **Unit** — `tests/test_core.py`:
   - `extract_candidates` open mode: stop-list filters
   - `extract_candidates` vocab mode: only known names
   - `_normalize` whitespace handling
   - `_PROPER_RX` matching of unicode and multi-word
3. **Boundary** — `tests/test_interface.py`:
   - `skry(...)` returns the shape promised in `INTERFACE.md`
4. **Integration** — `tests/test_skry.py`:
   - Full skry against a tiny test corpus (when test DB available)
5. **Regression** — `tests/test_regression.py`:
   - Any specific bug from `docs/bugs/` reproduces and stays fixed

---

## The Rite of Preservation (Commits)

```
<short subject under 70 chars>

<blank line>

<paragraph on the WHY>

Co-Authored-By: Claude Opus 4.7 (1M context) <noreply@anthropic.com>
```

## The Rite of Return

`git revert` for pushed commits. Never `git reset --hard` on shared
history.

---

## Plundering Workflow

Skry has plundered no upstream code. If a future feature does, follow the
[canonical workflow](https://github.com/hrabanazviking/Mythic-Engineering/blob/main/MYTHIC_ENGINEERING_PLUNDERING_WORKFLOW.md).
