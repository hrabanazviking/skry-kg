# Bug 0010: `extract_candidates()` handles both vocab and open modes in one function

**Discovered:** 2026-05-18 by Auditor
**Status:** RESOLVED 2026-05-18 (no code change — current design is correct for this library's size)

---

## Symptom

`extract_candidates()` is 31 lines and contains two distinct code paths
(vocab-restricted vs. open-vocabulary) with an `if/else` split. The
Auditor flagged it as a candidate for refactoring into two private
functions.

## Resolution

For Skry, **one function with two paths is the right shape**:

1. The entire library is ~200 lines. Adding two extra symbols for what
   amounts to a 15-line each branch would *reduce* readability, not
   increase it.
2. `extract_candidates` is also part of the public API
   (`skry.__all__` reexports it). Callers benefit from a single
   well-documented function with a clear `vocab=None` toggle, not from
   choosing between two undocumented internal helpers.
3. The function is still well under the Iron Law's 50-line guideline.

## Lessons

The 50-line rule is a guideline, not a fetish. Splitting a 30-line
function with a clean `if vocab: ... else: ...` into two functions plus a
dispatcher would add lines, not subtract them. The Auditor's role is to
flag candidates; the Architect's role is to judge.
