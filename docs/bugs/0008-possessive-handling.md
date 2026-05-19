# Bug 0008: Apostrophe handling fragments possessives and single-letter prefixes

**Discovered:** 2026-05-18 by Auditor
**Status:** RESOLVED 2026-05-18 (no code change — documented as intentional trade-off)

---

## Symptom

The proper-noun regex treats `'` as a token separator within a name,
which means:

- `"Odin's Throne"` extracts as `["Odin", "Throne"]` — possessive splits.
- `"O'Brien"` extracts as `["Brien"]` only — the `O` alone fails the inner
  `[a-zà-ÿß]+` quantifier (needs 2+ letters).
- `"D'Artagnan"` — same problem.

## Resolution

This is an **intentional trade-off**:

1. We chose to support multi-word compound names like `"Sif Gold-Hair"`,
   which is common in mythological corpora.
2. The same character class that enables that also includes `'` as a
   separator, which fragments possessives. To detect possessives we'd
   need lookahead/lookbehind grammar that distinguishes `Odin's` (split)
   from `O'Brien` (don't split) — non-trivial and noisy.
3. Possessive fragmentation has a *harmless side effect*: in Skry's open
   mode, "Odin" and "Throne" both count as candidate entities, both get
   their similarity scores, both surface in results when relevant. The
   semantic link "Odin's Throne is Odin's" is lost but the two terms
   still appear in the neighborhood.
4. Single-letter-prefix names (`O'Brien`) are not Norse-corpus blockers
   and remain a known limitation, deferred until someone needs them.

## Lessons

Regex-based NER is a constant Pareto trade-off. For corpora that need
proper possessive/short-prefix handling, the right path is to install
Skein (which uses LLM-driven vocabulary discovery with aliases) and let
Skry's vocab mode handle disambiguation.
