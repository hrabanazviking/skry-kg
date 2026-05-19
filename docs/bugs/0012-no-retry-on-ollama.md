# Bug 0012: `_embed_one()` does not retry on Ollama transient failure

**Discovered:** 2026-05-18 by Auditor
**Status:** RESOLVED 2026-05-18 (no code change — contract is "raise to caller")

---

## Symptom

`_embed_one()` makes one POST to `/api/embed` and raises any `httpx.HTTPError`
straight to the caller. A single network blip kills the query.

## Resolution

This is **by design**:

1. Per `PHILOSOPHY.md` and `INTERFACE.md`, Skry's contract is to raise on
   external failures. The caller (Bifröst's `/api/skry` endpoint, or any
   library user) is responsible for retry policy.
2. Retry-on-transient logic at the library level would add state and
   policy. Skry's identity is "no state, no policy, no surprise."
3. The bifrost viewer wraps `/api/skry` in `@safely(...)` and returns the
   error to the browser, which can re-issue. That's the right layer.

By contrast, Skein DOES have retry (see `skein-kg`'s bug 0008): because
Skein runs for 15+ minutes and a single network blip wasting that work is
bad. Skry queries are ~100ms; a retry from the caller is fine.

## Lessons

Different libraries warrant different fault tolerance postures. Skein:
batch tool that owns 15 minutes of compute → internal retry. Skry: live
function call that owns 100ms → raise to caller. Both follow the Law of
Fault Tolerance; they implement it differently because their cost
profiles differ.
