# PROJECT_LAWS.md — Skry
## *Immutable Rules*

---

## Law of No Precomputation

There is no batch step. There is no `skry build`. There is no warmup. The
act of calling `skry(...)` is the entire computation. Any future contribution
that adds a precomputation phase is not Skry — it is a different tool.

## Law of No Storage

Skry writes to no tables, no files, no in-process caches that outlive a
single function call. (Per-call locals are fine. Module-level caches are
not.) The corpus and Skein's tables are the only persisted state Skry knows
about, and Skry reads them; it does not change them.

## Law of No Generation

Skry calls the embedding endpoint **once per query**. Skry does not call any
generative chat endpoint, ever. If a feature would require an LLM to write
text, it belongs in a different tool.

## Law of the Sacred Source

Skry's database access is strictly read-only. `chunks` is read. `documents`
is joined. `skein_entities` is read if it exists. No `INSERT`, no `UPDATE`,
no `DELETE`, no schema-modifying statement may appear anywhere in this code.

## Law of the Honest Vocab Mode

Every Skry response includes `vocab_mode: "skein"` or `vocab_mode: "open"`.
The caller is never left wondering which substrate produced the answer.
This field is part of the public contract.

## Law of Sourced Results

Every entity in the response carries `chunks: [int, ...]` — the evidence
chunk IDs that justified its inclusion. No entity may be returned without
at least one evidence chunk.

## Law of Fault Tolerance

If Ollama is unreachable, `skry()` raises a clear exception immediately —
there is nothing meaningful to return without the query embedding. If the
DB is unreachable, same. If the vocab lookup fails partway, fall back to
open mode and log a warning. The library never returns silently degraded
results.

## Law of the Public Surface

The functions in `skry/__init__.py` form the public API. They are
version-stable. Internal helpers in `skry.core` may change freely.

## Law of Single Responsibility

Skry projects entity neighborhoods. Skry does not:
- visualize anything (Bifröst's job),
- build static graphs (Skein's job),
- run hybrid search (Bifröst's `/api/search` does that),
- generate text,
- maintain user state.

Refuse the urge to grow. Skry's value lives in being one function with one
job.

## Rite of Preservation

Commit messages: short subject (under 70 chars), blank line, paragraph on
the *why*. `Co-Authored-By` lines for pair work.

## Rite of Return

`git revert` over `git reset --hard` for anything pushed.
