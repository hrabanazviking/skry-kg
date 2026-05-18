# Bug 0006: Embedding-model mismatch produces garbage; not warned

**Discovered:** 2026-05-18 by Auditor
**Status:** RESOLVED 2026-05-18

---

## Symptom

`skry(..., embed_model='X')` embeds the query with model X. If the corpus was embedded with model Y (and X != Y), the cosine similarities computed in the SQL are meaningless. If the dimensions happen to match, the query silently returns nonsense; if they don't, pgvector raises.

## Fix plan (additive)

Document loudly in PHILOSOPHY, INTERFACE, README, and in the `skry()` docstring:

> The `embed_model` argument MUST match the embedding model used to index the corpus. Mismatched models produce meaningless results — even when vector dimensions happen to coincide.

Future enhancement (not in this fix): a `corpus_metadata` table storing the indexer's `embed_model` and `embed_model_version`, validated at `skry()` start. Out of scope for this session.

## Lessons

When a library depends on an invariant that lives outside its repo, the library should at minimum *state* that invariant clearly. Silent failure on invariant violation is the worst kind of bug.
