# DATA_FLOW.md — Skry

> *Architect + Cartographer.*

---

## Entry Points

| # | Door | Format | Direction |
|---|------|--------|-----------|
| 1 | `chunks` table (Postgres, with `embedding vector(N)`) | rows | **In, read-only** |
| 2 | `documents` table (joined for `title`) | rows | **In, read-only** |
| 3 | `skein_entities` table (optional) | rows | **In, read-only** |
| 4 | `.env` (or env vars) | key=value | **In, config only** |
| 5 | The `query` argument to `skry()` | string | **In, per-call** |

Outgoing surfaces:

| # | Door | Format | Direction |
|---|------|--------|-----------|
| A | Return value of `skry()` | dict | **Out** |
| B | CLI stdout via `rich.console` | colored text | **Out** |

That's all. Skry writes nothing.

---

## The Single River — A Skry

```
skry(db_url, ollama_url=..., embed_model=..., query="Odin",
     top_chunks=60, top_entities=20, min_name_len=3)

   1. _embed_one(client, ollama_url, embed_model, query)
        POST {ollama_url}/api/embed  →  embedding vector

   2. open psycopg connection (per-call; closes at end)
      register_vector(conn)

   3. retrieve_chunks(conn, embedding, k=top_chunks)
        SELECT c.id, c.text, 1 - (c.embedding <=> emb::vector) AS sim,
               d.id, d.title
        FROM chunks c JOIN documents d ON c.document_id = d.id
        ORDER BY c.embedding <=> emb::vector
        LIMIT k
        returns list of (id, text, sim, doc_id, doc_title)

   4. _known_vocab(conn)
        if skein_entities table exists:
            SELECT name_norm, name FROM skein_entities
            returns {name_norm: canonical_name}
        else:
            returns None  (open-vocabulary mode)

   5. for each row in retrieved chunks:
        extract_candidates(text, vocab, min_name_len)
          if vocab provided:
            scan vocab regex against text → list of canonical names found
          else:
            _PROPER_RX.findall(text) → list of Title-Case sequences
            filter out _STOP_SURFACE entries
            filter out len < min_name_len
        for each candidate (dedup per chunk):
          if name.lower() == query.lower(): skip
          counts[key] += 1
          sim_sum[key] += sim
          chunks_by_entity[key].append(chunk_id) (cap at 5 samples)
          docs_by_entity[key].add(doc_id)

   6. for each entity:
        mean_sim = sim_sum / count
        score = count × mean_sim
        canonical_name = vocab[key] if vocab else key.title()

   7. sort by score descending; slice top_entities

   8. return {
        query, top_chunks, vocab_mode: "skein" | "open",
        entities: [{name, count, mean_sim, score, chunks, n_docs}, ...],
        evidence_chunk_ids: [first 10 retrieved chunk ids]
      }

   connection closes via with-block
```

That is the entire data flow. There are no caches, no background threads,
no subprocess, no side effects.

---

## Storage Locations and Lifecycles

| Storage | Owner | Skry's relationship |
|---|---|---|
| `chunks` table | parent ingest project | **read** during retrieval |
| `documents` table | parent ingest project | **read** (JOIN for `title`) |
| `skein_entities` table | Skein library (if built) | **read** (optional vocab filter) |
| `.env` | operator | **read** at process start |

Nothing else exists. Nothing gets written.

---

## Boundary Crossings

| # | From | To | Format |
|---|------|----|--------|
| 1 | caller | `skry()` | function arguments (str query + config) |
| 2 | `skry()` | Ollama | POST `/api/embed` with `{model, input: [query]}` |
| 3 | Ollama | `_embed_one` | JSON response with `embeddings[0]` |
| 4 | `skry()` | Postgres | `SELECT ... ORDER BY embedding <=> %s::vector LIMIT k` |
| 5 | Postgres | `retrieve_chunks` | rows of `(id, text, sim, doc_id, doc_title)` |
| 6 | `skry()` | Postgres (optional) | `SELECT name_norm, name FROM skein_entities` |
| 7 | `extract_candidates` | aggregator | list of canonical names per chunk |
| 8 | `skry()` | caller | dict with entities + evidence |

---

## Failure Modes

| Failure | Where caught | Behavior |
|---|---|---|
| Ollama unreachable | `_embed_one` raises `httpx.HTTPError` | Propagates to caller. Skry cannot answer without an embedding; this is appropriate. |
| Postgres unreachable | `psycopg.connect` raises | Propagates. Same logic. |
| `skein_entities` exists but empty | `_known_vocab` returns `{}` | Skry runs in vocab mode with zero matches; all results come back via `extract_candidates`'s "for key in vocab" fallthrough. Effectively yields nothing — by design. Without Skein vocab and an empty table, the operator should consider re-building Skein. |
| Query embedding is empty / zero-norm | downstream Postgres returns no useful order | Skry returns whatever order Postgres gives, with low similarity scores. Caller can detect via the low `mean_sim` values. |
| Query matches one of the corpus entity names exactly | the `query_key == key: skip` line | The query entity is excluded from its own neighborhood (correct behavior). |
| `chunks.embedding` dimension mismatches the query | pgvector raises | Propagates. The corpus and query embedding must come from the same model. |

There is intentionally no `try/except` wrapping the top-level `skry()`
function. Library callers are expected to handle their own exceptions.
HTTP layers (e.g. Bifröst's `/api/skry`) translate exceptions into HTTP
errors at their boundary.
