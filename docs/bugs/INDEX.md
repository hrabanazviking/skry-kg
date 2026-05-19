# docs/bugs/INDEX.md — Skry

> Bug notes from Auditor passes.

**Last Auditor pass:** 2026-05-18 (Sólrún Hvítmynd, session 2)

---

## Open

_None. As of session 3 the entire known bug backlog is closed — 12/12
resolved across two same-day sessions._

## Resolved (Session 2 — 2026-05-18)

| # | Title | Severity | File | Note |
|---|---|---|---|---|
| 0001 | Uppercase Þ excluded from proper-noun regex | high | `skry/core.py:35` | [bug](0001-thorn-regex-gap.md) |
| 0002 | Vocab lookup not wrapped; Law of Fault Tolerance broken | high | `skry/core.py:122` | [bug](0002-vocab-lookup-unprotected.md) |
| 0003 | Public `skry()` function lacks docstring | medium | `skry/core.py:113` | [bug](0003-skry-docstring.md) |
| 0004 | No input bounds on `top_chunks` / `top_entities` / `query` length | medium | `skry/core.py:113-116` | [bug](0004-skry-input-bounds.md) |
| 0005 | Library uses no `logging`; warnings impossible | medium | `skry/core.py` (module) | [bug](0005-skry-no-logger.md) |
| 0006 | Embedding-model mismatch risk undocumented | medium | `skry/core.py` + INTERFACE.md | [bug](0006-embed-model-mismatch.md) |

## Deferred

_None. Backlog is empty._

## Resolved (Session 3 — 2026-05-18, "kill the backlog")

| # | Title | Severity | File | Note |
|---|---|---|---|---|
| 0007 | `documents.title` nullable; type hint promised `str` | low | `skry/core.py` | `retrieve_chunks` return type updated to `str | None` for the title field. Docstring notes the parent schema permits NULL. |
| 0008 | Apostrophe possessive handling | low | `skry/core.py` | Resolved as no-action — see [bug note](0008-possessive-handling.md). Intentional trade-off documented; vocab mode covers the gap. |
| 0009 | `evidence_chunk_ids` hard-coded to 10 | low | `skry/core.py` | Added `max_evidence_chunks` parameter (default 10, range 1..500). Documented in INTERFACE.md and validated. |
| 0010 | `extract_candidates` does both modes | low | `skry/core.py` | Resolved as no-action — see [bug note](0010-extract-candidates-size.md). 31 lines is fine; splitting would harm clarity. |
| 0011 | CJK proper nouns not matched | medium | `skry/core.py` | Added `_PROPER_RX_NON_LATIN` with patterns for CJK ideographs, Hiragana, Katakana, Hangul, Cyrillic Title-Case, Arabic, and Devanagari. `extract_candidates` now runs both passes. Tested on 龙王 / 孔子 / Свято Олег. |
| 0012 | No retry on Ollama embedding failure | low | `skry/core.py` | Resolved as no-action — see [bug note](0012-no-retry-on-ollama.md). Skry's contract is "raise to caller"; retry is the caller's policy. Skein's longer-running build has retry; Skry's 100ms queries don't need it. |

---

## Categories of issues found this session

- **1 silent-loss-of-data** bug (Þ missing from regex) → fixed by extending range
- **1 robustness gap** (vocab lookup not protected) → fixed with try/except + log
- **2 observability/doc gaps** (no docstring, no logger) → fixed
- **1 input-validation gap** → fixed with bound checks
- **1 doc-honesty gap** (embedding-model mismatch silent) → fixed in PHILOSOPHY + INTERFACE

Skry's design discipline held up well — the audit found no violations of
its core iron laws (no precomputation, no storage, no generative LLM,
read-only). The findings are around defensive hardening and honesty.
