# Bug 0003: Public `skry()` function has no docstring

**Discovered:** 2026-05-18 by Auditor
**Status:** RESOLVED 2026-05-18

---

## Symptom

`def skry(...)` — the function exported as the *entire* public API has no docstring. Developers reading the code need to flip to INTERFACE.md to understand it.

## Fix plan (additive)

Add a docstring covering: one-line summary, params with types, return shape, exceptions raised (httpx + psycopg), one-line example, link to INTERFACE.md.

## Lessons

The most-used function should be the best-documented in-source.
