# DOMAIN_MAP.md — Skry
## *Cartography of Realms*

> Skry is small. The map is short. Both should stay that way.

---

## The Realms

### 1. The Seer — `skry/core.py`

**Responsibility:** The single function `skry(...)` and its small helpers
(`retrieve_chunks`, `extract_candidates`). The actual projection logic:
embed → retrieve → extract → rank → return.

**Knows about:** psycopg, pgvector, httpx (one embed call per query),
numpy (light use), the `_PROPER_RX` regex, the `_STOP_SURFACE` stop-list.

**Forbidden from:**
- Calling any chat / generative LLM endpoint.
- Persisting state.
- Maintaining caches.
- Reaching beyond the public columns of `chunks` and (optionally)
  `skein_entities`.

### 2. The Command Door — `skry/cli.py`

**Responsibility:** Typer-based CLI: `look <name>`, `search <phrase>`. Loads
`.env`, formats output with Rich.

**Knows about:** Typer, Rich, `skry.core.skry`.

**Forbidden from:**
- Implementing any algorithm logic.
- Reading or writing the database directly.

### 3. The Public API — `skry/__init__.py`

**Responsibility:** Reexports `skry`, `retrieve_chunks`, `extract_candidates`.

**Forbidden from:** reexporting helpers that are not in `__all__`.

### 4. The Deep Memory — Postgres (read-only from Skry)

**Responsibility:** `chunks` (mandatory), `skein_entities` (optional, used as
a vocabulary filter).

**Forbidden from (Skry's perspective):** any modification whatsoever. Skry
has zero write capability by design.

---

## What This Library Owns

**Nothing.** Skry has no tables, no caches, no files outside its own source.

## What This Library Reads

```
chunks (id, text, embedding, document_id)  — mandatory
documents (id, title)                       — joined for context
skein_entities (name_norm, name)            — optional; turns on vocab mode if present
```

## What This Library Writes

```
nothing.
```

---

## Why these boundaries

Skry's value proposition is *no precomputation*. Any state — even a tiny
in-memory cache — drifts from the corpus the moment the corpus changes. By
owning nothing, Skry can never go stale.

The optional `skein_entities` dependency is exactly that — optional. If
Skein has been built, Skry uses its vocabulary as a precision filter; if
not, Skry falls back to open-vocabulary regex over proper nouns. Both
modes are first-class and both are explicitly reported in the response.

The CLI/algorithm split is the same wisdom as Skein's: humans use the CLI;
other code uses the function. Neither should reach into the other's realm.
