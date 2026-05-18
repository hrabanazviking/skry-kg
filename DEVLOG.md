# DEVLOG.md — Skry

> *Scribe. Append-only.*

---

## 2026-05-18 — Inception

**Crew:** Volmarr Wyrd (Architect-in-chief), Claude Opus 4.7 (Master
Craftsman).

Skry was **invented** in this session as the query-time companion to
[Skein](https://github.com/hrabanazviking/skein-kg). The two were
co-invented together — Skein the static-graph half, Skry the live-lookup
half — both in response to the cost crisis of running llama-per-chunk KG
extraction on a 6 GB laptop GPU.

### The framing

Where Skein asks: *can we build a knowledge graph without per-chunk LLM
calls?* Skry asks: *can we skip the build entirely?*

The observation: the implicit graph already exists in the embeddings. A
precomputed KG is one *projection* of that implicit graph. The projection
takes time to build and goes stale on every new ingest. So instead — do
the projection on demand, slice by slice, per query.

### Implementation

- `skry/core.py` — one user-facing function (`skry()`) plus two helpers
  (`retrieve_chunks`, `extract_candidates`). Plus a small stop-list and a
  proper-noun regex.
- `skry/cli.py` — typer-based CLI: `look <name>`, `search <phrase>`.
- `skry/__init__.py` — reexports the public surface.

Total source: ~180 lines including comments and docstrings. Skry is
deliberately the smallest of the three repos.

### Pipeline (recap from DATA_FLOW.md)

1. Embed query once via Ollama
2. Postgres top-K chunks by cosine
3. Optional: load Skein vocabulary as precision filter
4. Lazy regex NER on retrieved chunks
5. Rank by `count × mean_similarity`
6. Return entity list with evidence chunk ids

Typical wall time: ~100 ms on the reference corpus (~23 000 chunks, Skein
vocabulary present).

### Why "Skry"

Scrying is the practice of looking into a reflective medium (water, a
crystal, a polished disc) to see things distant or hidden. Skry's medium
is the embedding space; the "hidden things" are the entity neighborhoods
implicit in it. The name pairs with Skein (a coil of thread / a flock of
geese) under the alliterative "Sk-" prefix and the shared Norse mythic
theming.

### Smoke test on Volmarr's corpus

Running `skry "Odin"` against the live corpus returned (in 75 ms, vocab
mode = skein):

```
Galdr   (8 mentions across 3 docs · score 5.064)
wyrd    (6 mentions across 2 docs · score 3.819)
Freyja  (5 mentions · ...)
```

All three are genuinely related to Odin in Norse mythology. Quality is
high because Skein's vocabulary acts as a precision filter — the regex
isn't picking up arbitrary capitalized words.

### Decisions

- **Why no caching of any kind?** Caching introduces state. State goes
  stale. Skry's value is freshness. The 100 ms uncached query is fast
  enough.
- **Why open-vocabulary fallback?** So Skry works even before Skein has
  been built. Quality is lower (proper-noun regex picks up "Tuesday
  Morning") but the tool functions out of the box.
- **Why not call an LLM?** Generative LLM calls are the cost we built
  Skry to avoid. The embedding model is enough.
- **Why expose `retrieve_chunks` and `extract_candidates`?** So a caller
  who wants a Skry-shaped query but custom ranking can compose those
  pieces. They're stable enough to be public.

### Published

MIT-licensed public repo at
[`hrabanazviking/skry-kg`](https://github.com/hrabanazviking/skry-kg).
Initial commit + ME docs (SYSTEM_VISION, DOMAIN_MAP, ARCHITECTURE,
PROJECT_LAWS, INTERFACE, skry/README_AI) pushed in the same session.

### Lessons recorded

1. **Refusal is a feature.** Refusing to add a cache, a build step, or an
   LLM call is what gives Skry its identity.
2. **Composability beats monolith.** Skry uses Skein's vocab if present;
   neither knows about the other directly. Loose coupling via the schema.
3. **Small libraries should stay small.** The temptation to grow Skry into
   "Skry+" with batch mode and ranking variants would dissolve its
   reason to exist.

### Open threads

- Auditor pass on `core.py` per the Mythic Engineering bug-hunt rite.
- Invariant tests under `tests/`.
- Consider: should the open-vocabulary stop-list be configurable via env?
- Consider: how does Skry behave at very large `top_chunks` (e.g. 500)?
  Linear regex cost; should be fine but worth measuring.

---

## 2026-05-18 — Session Two: Full Mythic Engineering Treatment

Architect pointed at the canonical Mythic Engineering repo and asked for
full doctrine + bug hunt + robustness rites. This session adds
PHILOSOPHY, DATA_FLOW, DEVLOG (this file), MYTHIC_ENGINEERING, the
Auditor's bug notes under `docs/bugs/`, and the first round of invariant
tests.
