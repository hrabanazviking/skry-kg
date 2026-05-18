# ARCHITECTURE.md — Skry
## *The Bones of the World*

---

## Layout

```
skry-kg/
├── pyproject.toml      ← uv manifest; declares `skry` console script
├── README.md           ← Outward-facing intro
├── LICENSE             ← MIT
├── .env.example        ← Template
├── SYSTEM_VISION.md    ← The soul
├── DOMAIN_MAP.md       ← Realm boundaries
├── ARCHITECTURE.md     ← This document
├── PROJECT_LAWS.md     ← Immutable rules
├── INTERFACE.md        ← Public Python API contract
└── skry/
    ├── __init__.py     ← Reexports public surface
    ├── core.py         ← The seer (one function + helpers)
    ├── cli.py          ← typer-based CLI
    └── README_AI.md    ← Notes for AI maintainers
```

---

## The One Function

```
                      ┌─────────────────────────────┐
                      │  query: "Odin"              │
                      └──────────────┬──────────────┘
                                     │
                                     ▼
              ┌───────────────────────────────────────┐
              │  embed query (1 ollama embed call)    │
              └──────────────┬────────────────────────┘
                             │
                             ▼
              ┌───────────────────────────────────────┐
              │  SELECT top-K chunks by cosine        │ ← Postgres pgvector
              │  (default K=60)                       │
              └──────────────┬────────────────────────┘
                             │
                             ▼
              ┌───────────────────────────────────────┐
              │  optional: load skein_entities vocab  │
              │  (one-shot SELECT, cached per call)   │
              └──────────────┬────────────────────────┘
                             │
                             ▼
              ┌───────────────────────────────────────┐
              │  for each chunk:                      │
              │    extract candidates                 │
              │     - if vocab present: known-name     │
              │       matches only (high precision)   │
              │     - else: proper-noun regex + stop  │
              │       list (open vocabulary)          │
              └──────────────┬────────────────────────┘
                             │
                             ▼
              ┌───────────────────────────────────────┐
              │  aggregate per entity:                │
              │    count, mean_similarity,            │
              │    evidence_chunks, n_docs            │
              └──────────────┬────────────────────────┘
                             │
                             ▼
              ┌───────────────────────────────────────┐
              │  rank by (count × mean_sim)           │
              │  return top-N (default N=20)          │
              └───────────────────────────────────────┘
```

Total: one embed call, one SELECT, one optional SELECT for vocab, and pure
Python aggregation. Typical wall time ~100 ms on the reference hardware
(20k chunks, vocab present).

---

## Rivers of Flow

### River of a Skry

```
skry("Odin")
   → embed via Ollama
   → Postgres top-K chunks (pgvector cosine, IVF/HNSW)
   → check skein_entities exists → load vocab if so
   → loop over chunks: regex / vocab match → candidate names
   → aggregate counts + similarities
   → sort by score, slice top-N
   → return {query, vocab_mode, entities[], evidence_chunk_ids[]}
```

That is the entire flow.

---

## Key Connectors

| From | To | Protocol |
|------|----|----------|
| `skry.core` | Postgres | `psycopg` (one connection per `skry()` call) |
| `skry.core` | Ollama | `httpx` POST `/api/embed` (single embedding) |
| `skry.cli` | `skry.core` | Python import |
| External callers | `skry.*` | imports listed in `__init__.py` |

---

## Why this design is fast

- **One embedding** per query (not per chunk).
- **One database round trip** for the top-K chunks (pgvector with an HNSW
  index makes this O(log N) in practice).
- **One additional round trip** for the vocab table (~few hundred rows,
  cached in the connection for the duration of the call).
- **Pure-Python aggregation** over a few dozen short strings — trivially
  fast.

There is no operation in Skry that scales worse than `O(top_chunks * avg_chunk_chars)`,
because the regex scan touches only the chunks that came back from the top-K
retrieval.

## Why this design is fresh

Because Skry has no cache, the moment a chunk is committed to the database
it can show up in a Skry result. There is no "ingest → wait for rebuild"
gap that a precomputed graph would have.

---

## What can change safely

- The default `top_chunks` and `top_entities` parameters.
- The `_STOP_SURFACE` set of strings (extend with corpus-specific noise).
- The `_PROPER_RX` regex (carefully).
- New CLI commands.

## What must NOT change without redrawing this map first

- The function signature in `INTERFACE.md`.
- The shape of the returned dict (other consumers depend on the keys).
- The vocab-mode toggle (Skein-present vs Skein-absent). Both paths are
  load-bearing.
