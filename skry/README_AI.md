# skry/ — README_AI.md

This directory is **The Seer** (see `../DOMAIN_MAP.md`). It is intentionally
small.

## What's here

- `__init__.py` — reexports `skry`, `retrieve_chunks`, `extract_candidates`.
  Updating this list requires a corresponding update to `../INTERFACE.md`.
- `core.py` — the one function plus two helpers. The whole library is
  smaller than its docs.
- `cli.py` — Typer-based CLI: `look`, `search`. Strictly presentation.

## What touches the LLM

- One call to `ollama/api/embed` per `skry()` invocation, embedding the
  query string. That's it.

## What does NOT touch the LLM

- Everything else. Candidate extraction is regex. Aggregation is plain
  Python. Ranking is numpy-free arithmetic over short lists.

## How to make changes

1. **New CLI verb.** Add to `cli.py`. Do not put any algorithm logic there.

2. **Tune the open-vocab regex.** Edit `_PROPER_RX` in `core.py`. Test
   carefully — false positives become noise; false negatives become missing
   entities.

3. **Add to the stop-list.** Append to `_STOP_SURFACE`. Useful for
   corpus-specific noise terms that keep showing up.

4. **Optional: swap regex for a small NER model.** Allowed, as long as the
   public function signatures and return shape stay identical. The whole
   point of `INTERFACE.md` is that consumers can rely on the contract while
   the substrate changes.

## What to never do

- Add a precomputation/batch step. (See Law of No Precomputation.)
- Add a generative LLM call. (See Law of No Generation.)
- Cache anything past the duration of a single function call. (See Law of
  No Storage.)
- Write to any database table. (See Law of the Sacred Source.)
- Return entities without `chunks: [...]`. (See Law of Sourced Results.)

## When to refuse a feature request

If someone asks for:
- "Skry but it remembers what you asked yesterday" → no. Skry has no
  storage. Build a separate cache on the consumer side.
- "Skry that generates a paragraph explanation" → no. Skry does not
  generate. Send the result to an LLM in the consumer code.
- "Skry that builds a graph over time" → no. That's Skein's job; Skry
  reads it.

These refusals protect the library's identity. Without them, Skry becomes
"another KG tool" and the entire reason for its existence dissolves.
