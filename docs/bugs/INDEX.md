# docs/bugs/INDEX.md — Skry

> Bug notes from Auditor passes.

**Last Auditor pass:** 2026-05-18 (Sólrún Hvítmynd, session 2)

---

## Open

_none — all P0/P1 from session 2 have been promoted to dedicated notes and
fixed additively this session._

## Resolved (Session 2 — 2026-05-18)

| # | Title | Severity | File | Note |
|---|---|---|---|---|
| 0001 | Uppercase Þ excluded from proper-noun regex | high | `skry/core.py:35` | [bug](0001-thorn-regex-gap.md) |
| 0002 | Vocab lookup not wrapped; Law of Fault Tolerance broken | high | `skry/core.py:122` | [bug](0002-vocab-lookup-unprotected.md) |
| 0003 | Public `skry()` function lacks docstring | medium | `skry/core.py:113` | [bug](0003-skry-docstring.md) |
| 0004 | No input bounds on `top_chunks` / `top_entities` / `query` length | medium | `skry/core.py:113-116` | [bug](0004-skry-input-bounds.md) |
| 0005 | Library uses no `logging`; warnings impossible | medium | `skry/core.py` (module) | [bug](0005-skry-no-logger.md) |
| 0006 | Embedding-model mismatch risk undocumented | medium | `skry/core.py` + INTERFACE.md | [bug](0006-embed-model-mismatch.md) |

## Deferred (open in index, fix later)

| # | Title | Severity | File | Reason for deferral |
|---|---|---|---|---|
| 0007 | `documents.title` may be NULL; type hint promises `str` | low | `skry/core.py:50-51` | Cosmetic; rare in well-formed corpora. |
| 0008 | Apostrophe handling fragments possessives ("Odin's Throne") | low | `skry/core.py:35` | Intentional trade-off for O'Brien-style names. Documented. |
| 0009 | `evidence_chunk_ids` hard-coded to 10 | low | `skry/core.py:162` | Documented in INTERFACE.md; configurable in future minor version. |
| 0010 | `extract_candidates` does both vocab and open mode | low | `skry/core.py:80-110` | 31 lines, well under 50; pragmatic single-function design preserved. |
| 0011 | CJK proper nouns won't match the regex | medium | `skry/core.py:35` | Same root as skein 0001; deferred until both can be fixed with a shared approach. |
| 0012 | No retry on Ollama embedding failure | low | `skry/core.py:42-46` | Skry's contract is "raise on failure"; retry is the caller's job. Documented in PHILOSOPHY. |

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
