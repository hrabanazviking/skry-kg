# Skry

> *see what an entity is woven into*

Skry is a **query-time** entity-neighborhood projection over an existing vector store. There is no precomputed knowledge graph: when you ask "what is Odin connected to?", Skry computes the answer on the fly in ~100 ms.

Companion project: [`skein-kg`](https://example.invalid/skein-kg) — the static woven graph.

## The trick

A conventional KG extraction pipeline reads every chunk through an LLM and writes structured triples to a database. Skry inverts that: **the graph already exists implicitly in your embeddings.** Skry just projects a slice of it on demand.

When you ask about an entity `E`:

1. **Embed** the entity name and run a semantic search against `chunks` (top-K, e.g. 60).
2. **Lazy NER**: cheap regex over those K chunks to find proper-noun candidates (Title-Case word sequences not in a stop-list). Optionally restrict candidates to a known entity vocabulary (e.g. one built by Skein) for cleaner results.
3. **Rank** each co-occurring entity by `(appearance_count × mean_chunk_similarity)`.
4. **Return** the top-N entities with their evidence chunk IDs.

No batch, no overnight grind, no autoregressive generation. Works the instant a new document is ingested.

## Why "Skry"

Scrying is the practice of looking into a reflective medium — water, a crystal, a polished disc — to see things distant or hidden. Here the medium is the embedding space; the "things hidden" are the entity neighborhoods implicit in it.

## Inputs

Skry expects a Postgres database with the standard pgvector ingest layout:

```sql
documents (id, title, …)
chunks    (id, document_id, text, embedding vector(N), …)
```

If a `skein_entities` table is present (built by [`skein-kg`](https://example.invalid/skein-kg)), Skry uses it as a known-entity allow-list — much higher precision than open-vocabulary regex.

Skry writes nothing.

## Usage

```bash
cp .env.example .env
uv sync
uv run skry look "Odin"             # entity neighborhood, top 20 by default
uv run skry look "Mímir" --top 10
uv run skry search "the well of wisdom"   # neighborhood from a phrase, not a single entity
```

## API

```python
from skry import skry

result = skry(
    db_url="postgresql:///knowledge",
    ollama_url="http://localhost:11434",
    embed_model="nomic-embed-text",
    query="Odin",
    top_chunks=60,
    top_entities=20,
)
# {"query": "Odin", "entities": [{"name": …, "count": …, "score": …, "chunks": [...]}, ...]}
```

## Limits & honesty

- Open-vocabulary regex is noisy on its own — "Tuesday Morning" will be flagged as an entity. With a Skein vocabulary as filter, precision goes way up.
- It only sees entities co-occurring in the top-K retrieved chunks. Far-flung connections need a higher `top_chunks`.
- "Connection strength" is correlation in semantic space, not a typed relation. For typed predicates use Skein.

## Status

Co-invented by a user and Claude during a single session, May 2026. Lives at `~/ai/skry-kg/`. Open to becoming a real library if useful to others.

## License

MIT
