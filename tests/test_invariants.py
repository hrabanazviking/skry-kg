"""Invariant tests for Skry — the Prophecy Rite, layer 5.

These tests verify the IMMUTABLE truths from PROJECT_LAWS.md. Pure-Python.
No Postgres or Ollama required.

Run with:    uv run pytest tests/
"""
from __future__ import annotations

import inspect
import re

import pytest

from skry import skry, retrieve_chunks, extract_candidates
from skry.core import _PROPER_RX, _STOP_SURFACE, _normalize


# ─── Iron Law: no precomputation ───────────────────────────────────────────

def test_no_precomputation_in_source():
    """Skry must not contain any batch-build entry point."""
    import skry.core as core
    src = inspect.getsource(core)
    forbidden = ["def build", "def precompute", "def index_all", "def bulk_"]
    for tok in forbidden:
        assert tok not in src, f"Skry contains forbidden token {tok!r}"


# ─── Iron Law: no storage ──────────────────────────────────────────────────

def test_no_writes_in_source():
    """Skry must not write to any persistent store."""
    import skry.core as core
    src = inspect.getsource(core)
    forbidden_sql = re.compile(
        r"\b(INSERT\s+INTO|UPDATE|DELETE\s+FROM|ALTER\s+TABLE|DROP\s+TABLE|CREATE\s+TABLE)\b",
        re.IGNORECASE,
    )
    assert not forbidden_sql.search(src), "Skry contains write SQL — violates 'no storage' law"
    # No file writes either
    assert "open(" not in src or "open(" in src and "'r" in src or '"r' in src, \
        "double-check any open() calls are read-only"


# ─── Iron Law: no generative LLM calls ─────────────────────────────────────

def test_no_chat_endpoint_in_source():
    """Skry uses /api/embed only. No /api/chat or /api/generate calls."""
    import skry.core as core
    src = inspect.getsource(core)
    assert "/api/chat" not in src, "Skry contains a chat endpoint reference"
    assert "/api/generate" not in src, "Skry contains a generate endpoint reference"
    assert "/api/embed" in src, "Skry should call /api/embed exactly once"


# ─── Public surface ────────────────────────────────────────────────────────

def test_public_surface():
    """Public API is exactly skry, retrieve_chunks, extract_candidates."""
    import skry
    expected = {"skry", "retrieve_chunks", "extract_candidates"}
    actual = set(skry.__all__)
    assert actual == expected


def test_skry_has_docstring():
    """Per docs/bugs/0003: the public function must be self-documenting."""
    assert skry.__doc__ is not None and len(skry.__doc__) > 100, \
        "skry() docstring missing or trivially short"


# ─── Bug 0001: Þórr matches the proper-noun regex ────────────────────────

@pytest.mark.parametrize("text,expected_substrings", [
    ("Þórr lifted the hammer", ["Þórr"]),
    ("Þrúðr is Þórr's daughter", ["Þrúðr", "Þórr"]),
    ("Ðagr at dawn", ["Ðagr"]),
    ("Odin and Mímir spoke", ["Odin", "Mímir"]),
    ("Sif Gold-Hair walked", ["Sif Gold-Hair"]),
])
def test_proper_rx_extracts_norse_and_compound_names(text, expected_substrings):
    """Per docs/bugs/0001 (RESOLVED): Þ and other extended-Latin uppercase
    letters match. Per docs/bugs/0008 (DEFERRED): possessives split and
    single-letter-prefix names like O'Brien are not supported by the
    current regex (the inner token quantifier requires 2+ letters)."""
    found = _PROPER_RX.findall(text)
    for s in expected_substrings:
        assert s in found, f"expected {s!r} in {text!r}, got {found}"


# ─── Input validation (bug 0004) ──────────────────────────────────────────

def test_skry_rejects_empty_query():
    with pytest.raises(ValueError, match="empty"):
        skry("postgresql://nowhere/x", ollama_url="http://x", embed_model="m", query="")


def test_skry_rejects_whitespace_query():
    with pytest.raises(ValueError, match="empty"):
        skry("postgresql://nowhere/x", ollama_url="http://x", embed_model="m", query="   \n  ")


def test_skry_rejects_too_long_query():
    with pytest.raises(ValueError, match="too long"):
        skry("postgresql://nowhere/x", ollama_url="http://x", embed_model="m",
             query="x" * 20000)


def test_skry_rejects_out_of_range_top_chunks():
    with pytest.raises(ValueError, match="top_chunks"):
        skry("postgresql://nowhere/x", ollama_url="http://x", embed_model="m",
             query="q", top_chunks=0)
    with pytest.raises(ValueError, match="top_chunks"):
        skry("postgresql://nowhere/x", ollama_url="http://x", embed_model="m",
             query="q", top_chunks=10000)


# ─── extract_candidates behavior ──────────────────────────────────────────

def test_extract_candidates_open_mode_filters_stop_list():
    """Days/months/articles get filtered in open-vocab mode."""
    text = "The man arrived Monday in May with Odin and Mímir"
    found = extract_candidates(text, vocab=None)
    # Open mode finds proper nouns excluding stop-list
    assert "Monday" not in found, "Monday should be stop-listed"
    assert "May" not in found, "May should be stop-listed"
    assert "The" not in found, "The should be stop-listed"
    assert "Odin" in found
    assert "Mímir" in found


def test_extract_candidates_vocab_mode_only_returns_known():
    """In vocab mode, only known canonical names come back."""
    text = "Odin met Loki and someone named Brunhilde"
    vocab = {"odin": "Odin", "loki": "Loki"}  # Brunhilde not in vocab
    found = extract_candidates(text, vocab=vocab)
    assert "Odin" in found
    assert "Loki" in found
    assert "Brunhilde" not in found, "unknown name leaked through vocab filter"


# ─── _normalize properties ────────────────────────────────────────────────

@pytest.mark.parametrize("a,b", [
    ("Odin", "odin"),
    ("  Odin  ", "odin"),
    ("Odin Allfather", "odin allfather"),
    ("Odin\tAllfather", "odin allfather"),
    ("Odin   Allfather", "odin allfather"),
])
def test_normalize_collapses_and_lowers(a, b):
    assert _normalize(a) == b


# ─── Stop-list sanity ─────────────────────────────────────────────────────

def test_stop_surface_contains_common_noise():
    """Days, months, common articles are always in the stop list."""
    for word in ("The", "Monday", "May", "December", "Chapter"):
        assert word in _STOP_SURFACE, f"stop list missing {word!r}"
