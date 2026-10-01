# Skry technical manual

Source and CLI options verified on 2026-10-01. Skry projects an entity neighborhood
at query time from existing chunk embeddings. It is read-only: it neither ingests
documents nor builds persistent relations. Bifröst exposes it through `/api/skry`.

## 1. Requirements and role in the system

- Python 3.13+, uv and the frozen project dependencies.
- PostgreSQL/pgvector with standard `documents` and `chunks` source tables.
- Ollama with the **same embedding model/vector space** used for the corpus.
- Optional populated `skein_entities` for a known vocabulary.

Skry works before a Skein build exists, using open-vocabulary proper-name matching.
With a usable Skein vocabulary it restricts candidates to known names. New source
chunks can be retrieved immediately, but names absent from an older Skein vocabulary
may require a rebuild for vocabulary-mode discovery. An absent/unreadable vocabulary
falls back to open mode with a warning rather than failing the whole lookup.

The default Bifröst layout expects this checkout alongside `../ingest-viewer` and
`../skein-kg`. For the full stack, see
[the second-brain manual](../ingest-viewer/SECOND_BRAIN_MANUAL.md).

## 2. Install and configure

On a new checkout:

```bash
cd "$HOME/ai/skry-kg"
cp .env.example .env
chmod 600 .env
uv sync --frozen
```

Edit the private `.env` before querying. Do not overwrite an existing configured
file with the example. Required CLI configuration:

| Variable | Example/default | Meaning |
|---|---|---|
| `SKRY_DB_URL` | `postgresql:///knowledge` | Source database; a read-only account is sufficient |
| `SKRY_OLLAMA_URL` | `http://localhost:11434` | Embedding server; use the installed host |
| `SKRY_EMBED_MODEL` | `nomic-embed-text` | Match the stored corpus model |
| `SKRY_DB_CONNECT_TIMEOUT` | `5` | Connection setup timeout in seconds |

The CLI loads the root `.env`; existing process environment takes precedence.
`SKRY_TOP_CHUNKS`, `SKRY_TOP_ENTITIES` and `SKRY_MIN_NAME_LEN` in the example file
are not wired into the current CLI option defaults. Use `--chunks`/`--top` or Python
arguments explicitly. Library calls receive configuration as arguments and do not
load a dotenv automatically.

Do not use `scripts/setup-tailnet-db.sh` as a shortcut for outside-AI access.
That is direct database infrastructure setup and a separate privileged decision.
The supported external-client boundary is a scoped Bifröst key and its transport
policy, without giving the AI database or Ollama credentials.

## 3. Command-line use

```bash
uv run --frozen skry --help
uv run --frozen skry look "Odin"
uv run --frozen skry look "Mímir" --top 10 --chunks 60
uv run --frozen skry search "the well of wisdom" --top 15 --chunks 100
```

`look` takes a name; `search` takes a phrase. They call the same retrieval pipeline.
The defaults are `--chunks 60` and `--top 20`. More chunks broaden the evidence pool
and increase query cost; more entities only expand the output list. Neither option
adds or changes knowledge.

CLI/library query length is 1–10,000 characters, with a nonblank query required.
The library bounds `top_chunks` to 1–1000 and `top_entities` to 1–500. Bifröst's web
boundary is narrower: 1–500 chunks and 1–200 entities. Do not assume the largest
library value is accepted remotely.

## 4. Understand the result

The table shows `name`, `count`, `mean_sim`, `score`, `docs` and sample evidence IDs.
Candidates rank by occurrence count across retrieved chunks multiplied by mean
query/chunk similarity. A score is a relevance ranking, not calibrated confidence.

| Field | Meaning |
|---|---|
| `query` | Original query |
| `top_chunks` | Requested evidence pool size |
| `vocab_mode` | `skein` or `open` |
| `entities[].name` | Canonical candidate name |
| `count` | Retrieved-chunk appearances |
| `mean_sim`, `score` | Similarity and ranking score |
| `n_docs` | Distinct supporting documents in that retrieved pool |
| `chunks` | Sample evidence chunk IDs for that entity |
| `evidence_chunk_ids` | Overall sample of retrieval evidence |

Open mode can identify capitalized phrases that are not real entities. Skein mode
is cleaner but limited to its stored vocabulary. Unicode Norse names and possessive
handling have regression coverage; that does not make the regex a complete multilingual
named-entity recognizer. Inspect evidence before treating an association as a fact.
For typed relations, use Skein; Skry does not infer a precise causal predicate.

## 5. Python API

Run this complete example from the configured project root with `uv run --frozen
python YOUR_SCRIPT.py`, or embed it in an application that manages secrets safely:

```python
import json
import os
import sys
from dotenv import dotenv_values
from skry import skry

config = {**dotenv_values(".env"), **os.environ}
result = skry(
    config["SKRY_DB_URL"],
    ollama_url=config["SKRY_OLLAMA_URL"],
    embed_model=config["SKRY_EMBED_MODEL"],
    query="Odin",
    top_chunks=60,
    top_entities=20,
    min_name_len=3,
    max_evidence_chunks=10,
)
json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
```

`max_evidence_chunks` limits the overall returned sample and is capped by the
retrieved count. It does not change the source corpus. Invalid inputs raise
`ValueError`; DB/model failures propagate to the caller. The web host decides its
own HTTP response. Optional vocabulary lookup uses a rollback savepoint so a
failed query does not poison subsequent retrieval.

Lower-level `retrieve_chunks` and `extract_candidates` are documented in
[INTERFACE.md](INTERFACE.md). Use the high-level function unless you deliberately
need to own retrieval/ranking behavior.

## 6. Bifröst and outside AIs

In the viewer enable **SKRY**, type a query and press Enter. External readers call
`GET /api/skry?q=...&top_chunks=60&top_entities=20` with their own bearer key.
The call costs 10 weighted requests under default Bifröst limits. Read-only
permission is enough; it does not grant a rebuild or append capability.
Use the [AI protocol guide](../ingest-viewer/security/TECHNICAL_MANUAL.md) for auth,
transport, quotas and retry behavior.

Bifröst invokes Skry with its viewer DB/model configuration, not necessarily this
CLI's `SKRY_*` settings. Keep both configurations consistent when diagnosing a
CLI-versus-browser difference. Restart Bifröst after changing its own configuration.

## 7. Troubleshooting and verification

| Symptom | Likely boundary and action |
|---|---|
| CLI missing environment variable | Correct private root `.env`; all three required settings need values |
| Model unreachable/not found | Check configured Ollama host and installed model |
| Vector dimension error | Confirm source and query model; do not alter vectors just to silence it |
| Plausible but irrelevant results | Same-size different-model embeddings, corpus content or overly broad query |
| Noisy names | Check `vocab_mode`; build/rebuild Skein for a known vocabulary |
| Unexpected open mode | Read warning; inspect access to `skein_entities` and whether it is populated |
| Missing new name in Skein mode | Derived vocabulary predates new sources; schedule an owner Skein build |
| Few distant connections | Broaden query or increase `--chunks` within practical limits |
| Web 429 | Follow `Retry-After`; this is the host's admission policy |

```bash
uv run --frozen pytest -q
git status --short
```

No background Skry service or graph rebuild is required. It needs no independent
knowledge backup because it writes no knowledge; preserve its private configuration
and source revision with the [whole-stack backup](../ingest-viewer/SECOND_BRAIN_MANUAL.md#back-up-and-verify).
Treat returned text/evidence as private corpus data. See [ARCHITECTURE.md](ARCHITECTURE.md)
and [skry/README_AI.md](skry/README_AI.md) before implementation changes.
