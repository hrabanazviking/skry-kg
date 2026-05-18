# Bug 0002: `_known_vocab` raises propagate; Law of Fault Tolerance broken

**Discovered:** 2026-05-18 by Auditor
**Status:** RESOLVED 2026-05-18

---

## Symptom

`skry(...)` calls `_known_vocab(conn)` without a guard. If `skein_entities` exists but has unexpected schema (e.g. missing columns, renamed columns), the SELECT raises `psycopg.ProgrammingError` and the whole `skry()` call crashes — even though PROJECT_LAWS explicitly says "If the vocab lookup fails partway, fall back to open mode and log a warning."

## Expected

Vocab lookup failure → log warning → fall back to open-vocabulary mode.

## Invariant violated

PROJECT_LAWS — *Law of Fault Tolerance.*

## Fix plan (additive)

Wrap the call:
```python
try:
    vocab = _known_vocab(conn)
except Exception as e:
    log.warning("skry: skein vocab lookup failed (%s) — falling back to open mode", e)
    vocab = None
```
(See bug 0005 for adding the logger.)

## Lessons

Iron laws stated in PROJECT_LAWS must be reflected in code. A law without enforcement is decoration.
