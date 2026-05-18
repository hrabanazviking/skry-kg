# Bug 0004: No bounds on `query`, `top_chunks`, `top_entities`

**Discovered:** 2026-05-18 by Auditor
**Status:** RESOLVED 2026-05-18

---

## Symptom

`skry()` accepts unbounded `query` length and unbounded `top_chunks`/`top_entities`. A pathological caller can pass `top_chunks=1_000_000` (OOM risk) or `query=` (very long string).

## Fix plan (additive)

Add explicit validation at function start:
```python
if not query or not query.strip():
    raise ValueError("query must be non-empty")
if len(query) > 10000:
    raise ValueError("query too long (max 10000 chars)")
if not (1 <= top_chunks <= 1000):
    raise ValueError("top_chunks must be in [1, 1000]")
if not (1 <= top_entities <= 500):
    raise ValueError("top_entities must be in [1, 500]")
```

## Lessons

Library functions can be called by anyone. Defensive bounds are cheap.
