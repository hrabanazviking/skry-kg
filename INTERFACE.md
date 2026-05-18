# INTERFACE.md — Skry
## *Public Python API — Contract*

> This is the surface other code may rely on. Functions not listed here are
> private.

---

## Importing

```python
from skry import skry
# or
from skry import skry, retrieve_chunks, extract_candidates
```

---

## `skry(db_url, *, ollama_url, embed_model, query, top_chunks=60, top_entities=20, min_name_len=3) -> dict`

The seer's lookup. Embed a query, retrieve the most similar chunks, extract
co-occurring entities (open-vocabulary or Skein-filtered), rank them.

**Inputs:**
- `db_url` — libpq connection string for the host Postgres.
- `ollama_url` — base URL of the Ollama server.
- `embed_model` — name of the embedding model.
- `query` — the question or entity name to skry.
- `top_chunks` — how many chunks to retrieve from semantic search (default 60).
- `top_entities` — max entities to return (default 20).
- `min_name_len` — open-vocabulary mode: minimum length of a candidate
  proper noun (default 3; ignored in Skein-vocab mode).

**Outputs:**
```python
{
    "query": str,
    "top_chunks": int,
    "vocab_mode": "skein" | "open",
    "entities": [
        {
            "name": str,
            "count": int,
            "mean_sim": float,
            "score": float,
            "chunks": [int, ...],   # sample evidence chunk IDs (up to 5)
            "n_docs": int,
        },
        ...
    ],
    "evidence_chunk_ids": [int, ...],   # top 10 chunks that drove the result
}
```

**Side effects:** one Ollama `/api/embed` call, one Postgres top-K query,
optionally one Postgres SELECT against `skein_entities`. Nothing is written.

**Errors:**
- `HTTPException` style errors are not raised — Skry is a library, not an
  HTTP server. Callers handle exceptions.
- Raises `httpx.HTTPError` on Ollama failure.
- Raises `psycopg.OperationalError` on DB failure.
- Raises `HTTPException(400)`-equivalent: `httpx`/`psycopg` exceptions
  propagate; the host service (e.g. Bifröst's `/api/skry`) decides how to
  surface them to clients.

**Stability:** version-stable in 0.x.y. Adding new optional keyword
arguments is allowed; removing or renaming existing ones requires a major
version bump.

---

## `retrieve_chunks(conn, embedding, *, k) -> list[tuple[int, str, float, int, str]]`

Lower-level helper: given an open psycopg connection and an embedding,
return the top-K most similar chunks as `(id, text, similarity, doc_id,
doc_title)` tuples.

Useful if you want to compose a Skry-like flow with custom ranking or
custom candidate-extraction logic.

**Stability:** stable but considered semi-public. May gain optional kwargs.

---

## `extract_candidates(text: str, vocab: dict[str, str] | None, min_len: int = 3) -> list[str]`

Lower-level helper: given a chunk's text and optionally a known vocabulary
(`{name_norm: canonical_name}`), return the list of entity-name candidates.

In vocab mode, only known names are returned (high precision). In open
mode, proper-noun-shaped strings minus the stop-list (lower precision,
higher recall).

**Stability:** stable but considered semi-public.

---

## What is NOT public

- The `_PROPER_RX` regex, `_STOP_SURFACE` set, `_normalize(...)`,
  `_embed_one(...)`, `_known_vocab(...)`. These are implementation details.
- The internal layout of `extract_candidates`'s scoring path. Future
  versions may swap regex for a small NER model without changing the
  function's signature or contract.
