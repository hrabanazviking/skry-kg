# PHILOSOPHY.md — Skry

> *Written by the Skald.*

---

## The Wound This Project Salves

A precomputed knowledge graph is excellent for whole-graph visualization
and multi-hop traversal — but it has two costs that no marketing slide
mentions:

1. **It takes time to build.** Minutes for a small corpus; hours for a real
   one; days for the lazy llama-per-chunk pattern.
2. **It goes stale the moment you ingest a new document.** The graph you
   spent four hours building does not include the article you read this
   morning. To include it you must rebuild.

In a research workflow this is a deep problem. The whole point of
collecting text is to *integrate it into your understanding*. If the
"understanding artifact" (the graph) is frozen at the moment of the last
build, then every new ingestion creates a small gap between what you have
and what you can see.

Skry refuses the precomputation entirely. The act of *asking* — "what is
Odin connected to?" — *is* the computation. ~100 milliseconds per query.
Always fresh. Always reflects whatever is in the corpus right now.

---

## Core Ethos

**The graph already exists implicitly in the embeddings.** A precomputed KG
is one *projection* of that implicit graph. Skry does the projection on
demand, slice by slice.

**Freshness over completeness.** A query-time tool can never show you "every
connection that exists" — only "every connection in the top-K most-similar
chunks." But what it shows is *always current.* That trade-off is usually
the right one when the corpus is alive.

**Composable with precomputation, not opposed to it.** If [Skein](https://github.com/hrabanazviking/skein-kg)
has been run, Skry uses its entity vocabulary as a precision filter. The
two tools cooperate: Skein gives Skry a list of known names; Skry tells you
what those names are doing right now in the embedding-nearest chunks.

**No state to go wrong.** Skry has no caches, no batch step, no
"refresh" command. The only state it touches is the parent corpus's
`chunks` table (read) and optionally `skein_entities` (read). It cannot
become inconsistent because it owns no consistency to maintain.

---

## Values

| Value | What it means in practice |
|---|---|
| **Freshness** | Every query reflects the corpus at the moment of the query. No staleness. |
| **Honesty about substrate** | Every response includes `vocab_mode: "skein"` or `"open"`. The user always knows what produced the answer. |
| **Sourced results** | Every returned entity carries `chunks: [...]` — the evidence chunks. No claim without provenance. |
| **No state** | Skry writes nothing. It cannot rot. |
| **One function** | The entire library is a single user-facing function (`skry()`) and two helpers. Resisting growth is the discipline. |

---

## Iron Laws

1. **No precomputation.** Ever. There is no `skry build`. There will never
   be a `skry build`.

2. **No storage.** Skry writes to no tables, no files, no in-process caches
   that outlive a single function call.

3. **No generative LLM calls.** Skry uses the embedding endpoint exactly
   once per query. Generative chat is forbidden — that would re-introduce
   the cost we built Skry to avoid.

4. **Read-only against the parent corpus.** Skry's database access uses
   only `SELECT`. No `INSERT`, `UPDATE`, `DELETE`, or schema-modifying
   statements anywhere.

5. **Always report vocab mode.** Every response includes the `vocab_mode`
   field. The caller is never left wondering which substrate produced the
   result.

6. **Always source every claim.** Every entity in the response carries an
   `evidence_chunk_ids` array. No unsupported entries.

---

## Synthesis Approach

Skry is small on purpose:

- One Ollama embedding call per query (~50 ms)
- One Postgres top-K query via pgvector (~30 ms with HNSW index)
- One optional Postgres SELECT for the vocabulary (cached for the call)
- Pure-Python aggregation over a few dozen short strings (~5 ms)

That's the entire library. Two helpers (`retrieve_chunks`,
`extract_candidates`) are exposed for advanced composition; they are not the
star.

The novelty is not the math. The novelty is the **discipline of refusal**:
no batch, no storage, no generation, no growth. By being small, Skry can
be trusted not to surprise.

---

## What This Project Is Not

- **Not a knowledge-graph builder.** See [Skein](https://github.com/hrabanazviking/skein-kg).
- **Not a hybrid-search engine.** See Bifröst's `/api/search`.
- **Not a viewer.** See [Bifröst](https://github.com/hrabanazviking/bifrost-viewer).
- **Not an LLM caller** beyond the single per-query embedding.
- **Not a competitor to enterprise graph databases.** The query model is
  "given this query, what entities co-occur" — not "join three tables of
  triples."

---

## A Note on the Embedding Model

Skry compares the query embedding against the corpus embeddings stored in
`chunks.embedding`. **The embedding model must be the same on both sides.**
If you indexed your corpus with `nomic-embed-text` and then call
`skry(..., embed_model="bge-small")`, the cosine similarities will be
*meaningless* — even when the vector dimensions happen to match. Skry has
no way to detect this mismatch (the model used to embed the corpus is not
stored in the standard ingest schema), so it cannot warn you at runtime.

This is a **load-bearing invariant the library cannot enforce** —
operators must verify model consistency themselves. See
[`docs/bugs/0006-embed-model-mismatch.md`](docs/bugs/0006-embed-model-mismatch.md)
for the full discussion. A future enhancement (out of scope for this
version) would be a `corpus_metadata` table that stores the indexer's
model name, validated at `skry()` start.

---

## Ultimate Aim

That a user asking "what is this thing connected to?" can get a fast,
current, well-sourced answer without having paid the cost of building a
static graph — and that the answer is *good enough* to satisfy the question
most of the time, while remaining honest about the cases when it isn't.

If Skry ever grows a batch step, a cache, a generative call, or a write
endpoint: it has lost its identity. The correct response is to fork the
new behavior into a different repository and let Skry remain Skry.
