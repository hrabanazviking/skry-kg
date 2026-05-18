# Bug 0005: No logger in `skry/core.py`; warnings impossible

**Discovered:** 2026-05-18 by Auditor
**Status:** RESOLVED 2026-05-18

---

## Symptom

PROJECT_LAWS says "If the vocab lookup fails partway, fall back to open mode and log a warning." But `skry/core.py` doesn't `import logging`, so there's nowhere to log to.

## Fix plan (additive)

```python
import logging
log = logging.getLogger(__name__)
```
Use `log.warning(...)` where the laws require.

## Lessons

A library should set up a module-level logger as standard infrastructure. Callers control whether anything actually gets emitted by configuring handlers at the application level.
