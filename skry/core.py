"""Skry — see what an entity is woven into, on demand.

Given a query string (an entity name, or any phrase), Skry:
  1. Embeds the query and retrieves top-K most-similar chunks
  2. Extracts proper-noun candidates from those chunks (cheap regex + stop-list,
     OR restricted to a known vocabulary if a `skein_entities` table exists)
  3. Ranks candidates by appearance count × mean chunk similarity
  4. Returns the top-N entities with their evidence chunk IDs

No precomputation, no storage. Reads the existing chunks/embedding columns.
"""
from __future__ import annotations

import re
from collections import defaultdict

import httpx
import numpy as np
import psycopg
from pgvector.psycopg import register_vector


# Common single tokens (case-insensitive) to drop when we don't have a vocab.
# Kept small and conservative — vocab-restricted mode is the better answer.
_STOP_SURFACE = {
    "The", "A", "An", "In", "On", "At", "From", "To", "By", "For", "Of", "And", "Or",
    "But", "I", "We", "You", "He", "She", "It", "They", "This", "That", "These",
    "Those", "There", "Here", "Then", "When", "Where", "Why", "How", "Yes", "No",
    "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    "January", "February", "March", "April", "May", "June", "July", "August",
    "September", "October", "November", "December",
    "Chapter", "Section", "Page", "Volume",
}

_PROPER_RX = re.compile(r"\b[A-ZÀ-Ý][a-zà-ÿ]+(?:[ \-'][A-ZÀ-Ý][a-zà-ÿ]+)*\b")


def _normalize(s: str) -> str:
    return re.sub(r"\s+", " ", s.strip()).lower()


def _embed_one(client: httpx.Client, url: str, model: str, text: str) -> np.ndarray:
    r = client.post(f"{url}/api/embed", json={"model": model, "input": [text]}, timeout=120)
    r.raise_for_status()
    v = np.array(r.json()["embeddings"][0], dtype=np.float32)
    return v


def retrieve_chunks(
    conn: psycopg.Connection, embedding: np.ndarray, *, k: int,
) -> list[tuple[int, str, float, int, str]]:
    """Top-K chunks by cosine similarity. Returns (id, text, similarity, doc_id, doc_title)."""
    with conn.cursor() as cur:
        cur.execute(
            """
            SELECT c.id, c.text, 1 - (c.embedding <=> %s::vector) AS sim,
                   d.id, d.title
            FROM chunks c JOIN documents d ON c.document_id = d.id
            ORDER BY c.embedding <=> %s::vector
            LIMIT %s
            """,
            (embedding, embedding, k),
        )
        return cur.fetchall()


def _known_vocab(conn: psycopg.Connection) -> dict[str, str] | None:
    """If skein_entities exists, return {name_norm: canonical_name}. Else None."""
    with conn.cursor() as cur:
        cur.execute(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_name = 'skein_entities')"
        )
        if not cur.fetchone()[0]:
            return None
        cur.execute("SELECT name_norm, name FROM skein_entities")
        return {n: c for n, c in cur.fetchall()}


def extract_candidates(text: str, vocab: dict[str, str] | None, min_len: int = 3) -> list[str]:
    """Find proper-noun candidates in text. With vocab: only return known names."""
    found = _PROPER_RX.findall(text)
    if vocab is not None:
        out = []
        seen: set[str] = set()
        # Also try multi-word vocab keys via direct regex if not caught by proper-noun rx
        for surface in found:
            key = _normalize(surface)
            if key in vocab and key not in seen:
                out.append(vocab[key])
                seen.add(key)
        # Multi-token entities that don't all start with a capital may be missed
        # by the regex; scan vocab keys with word boundaries as a fallback.
        # (Cheap because vocab is typically a few hundred entries.)
        for key, canonical in vocab.items():
            if key in seen:
                continue
            if " " in key and re.search(rf"\b{re.escape(key)}\b", text, re.IGNORECASE):
                out.append(canonical)
                seen.add(key)
        return out
    # Open vocabulary: filter the surface list
    out = []
    for surface in found:
        if len(surface) < min_len:
            continue
        if surface in _STOP_SURFACE:
            continue
        out.append(surface)
    return out


def skry(
    db_url: str, *, ollama_url: str, embed_model: str, query: str,
    top_chunks: int = 60, top_entities: int = 20, min_name_len: int = 3,
) -> dict:
    with httpx.Client() as client:
        q_emb = _embed_one(client, ollama_url, embed_model, query)
    with psycopg.connect(db_url) as conn:
        register_vector(conn)
        rows = retrieve_chunks(conn, q_emb, k=top_chunks)
        vocab = _known_vocab(conn)

    # Aggregate per-entity stats: appearance count + mean similarity + sample chunks
    counts: dict[str, int] = defaultdict(int)
    sim_sum: dict[str, float] = defaultdict(float)
    chunks_by_entity: dict[str, list[int]] = defaultdict(list)
    docs_by_entity: dict[str, set[int]] = defaultdict(set)
    query_key = _normalize(query)

    for cid, text, sim, doc_id, _doc_title in rows:
        cands = extract_candidates(text, vocab, min_len=min_name_len)
        for name in set(cands):
            key = _normalize(name)
            if key == query_key:
                continue
            counts[key] += 1
            sim_sum[key] += float(sim)
            if len(chunks_by_entity[key]) < 5:
                chunks_by_entity[key].append(cid)
            docs_by_entity[key].add(doc_id)

    entities = []
    for key, c in counts.items():
        mean_sim = sim_sum[key] / c
        score = c * mean_sim
        # Recover canonical name: vocab wins, else first-seen surface
        canonical = vocab[key] if vocab and key in vocab else key.title()
        entities.append({
            "name": canonical, "count": c, "mean_sim": round(mean_sim, 3),
            "score": round(score, 3), "chunks": chunks_by_entity[key],
            "n_docs": len(docs_by_entity[key]),
        })
    entities.sort(key=lambda e: e["score"], reverse=True)
    entities = entities[:top_entities]

    return {
        "query": query,
        "top_chunks": top_chunks,
        "vocab_mode": "skein" if vocab else "open",
        "entities": entities,
        "evidence_chunk_ids": [r[0] for r in rows[:10]],
    }
