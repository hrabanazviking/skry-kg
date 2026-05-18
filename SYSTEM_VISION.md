# SYSTEM_VISION.md — Skry
## *The Genesis Scroll*

> *Sacred and unchanging.* If a future change to this project does not serve
> what follows, the change is wrong — not this scroll.

---

## Name and Nature

**Skry** — to see hidden things by looking into a reflective medium.

Skry is a Python library that answers entity-neighborhood questions about a
corpus *at query time*, with no precomputed knowledge graph and no storage of
its own. Given an entity name or any phrase, Skry projects the embedding-space
geometry into a small, focused list of "what is this woven into."

It is **not** a knowledge graph. It is **not** a search engine. It is a
projection — a momentary view of the implicit graph that already lives in the
vectors.

---

## Purpose — The Great Why

To make entity-centric exploration *instant* and *fresh*.

A precomputed knowledge graph is excellent for whole-graph visualization and
multi-hop traversal, but it has two costs: it takes time to build, and it
goes stale the moment you ingest a new document. Skry trades the up-front
build entirely — it computes nothing in advance — for ~100 millisecond
queries that always reflect the current state of the corpus, including
documents ingested seconds ago.

The aim is to make "what is X connected to?" feel like opening a drawer, not
running a job.

---

## Primary Rite — Core User Interaction

> ```bash
> uv run skry look "Odin"
> uv run skry look "Mímir" --top 10
> uv run skry search "the well of wisdom"
> ```

Or, used as a library:

```python
from skry import skry
result = skry(db_url, ollama_url=..., embed_model=..., query="Odin")
# {"query": "Odin", "entities": [{"name": "Mímir", "count": 8, ...}, ...]}
```

If the Primary Rite ever takes longer than a couple of seconds — wrong.

---

## Feeling / Vibe

- **Live, fluid.** A skry should feel like the corpus is *responding*, not
  retrieving from a slow cache.
- **Quietly accurate.** When a Skein vocabulary is present, Skry's results
  are noticeably cleaner — the seer has a name for things and ignores the
  rest.
- **Honest about its substrate.** Skry sees what is in the top-K retrieved
  chunks. If a connection lives only in document 47 and document 47 didn't
  make the cut, Skry will not surface it. Raise `top_chunks` to widen the
  gaze.

---

## Unbreakable Vows

1. **The Seer Shall Not Precompute.** Skry has no batch step. The act of
   asking *is* the work. No `skry build` command will ever be added.

2. **The Seer Shall Not Store.** Skry writes to no tables. It reads from
   `chunks` (always) and `skein_entities` (when present). It owns no
   database namespace.

3. **The Seer Shall Be Fast.** A skry against a corpus of 100,000 chunks
   should return in under a second on the reference hardware. If it doesn't,
   reduce `top_chunks`, not Skry's promise.

4. **The Seer Shall Be Fresh.** A document ingested one second ago must be
   visible in the next skry. There is no caching layer to invalidate.

5. **The Seer Shall Be Honest About Its Vocabulary.** When `skein_entities`
   exists, Skry says so in the response (`vocab_mode: "skein"`) and uses it
   as a precision filter. Without Skein, Skry falls back to open-vocabulary
   regex and says so (`vocab_mode: "open"`). The user always knows what
   substrate produced the answer.

6. **The Seer Shall Source Every Claim.** Every returned entity carries
   `chunks: [...]` — the evidence chunks where it was seen.

---

## What This Project Is Not

- Not a knowledge-graph builder. (See [`skein-kg`](https://github.com/hrabanazviking/skein-kg).)
- Not a hybrid-search engine. (See `/api/search` in the Bifröst viewer.)
- Not a 3D viewer. (See Bifröst.)
- Not an LLM caller, except for the single embedding of the query string.
  Skry does not generate text.

Skry is **one function**: take a query, return a ranked list of
co-occurring entities with their evidence. Resist every urge to grow.
