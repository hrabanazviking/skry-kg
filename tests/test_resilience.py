"""Behavioral regressions for malformed service data and vocabulary lookup."""
import httpx
import numpy as np
import pytest

from skry.core import _embed_one, extract_candidates


@pytest.mark.parametrize("vectors", [[], [[0, 0]], [[float('nan'), 1]], [[1], [2]], [None]])
def test_bad_query_vectors_are_rejected(vectors):
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"embeddings": vectors}))
    with httpx.Client(transport=transport) as client, pytest.raises((ValueError, TypeError)):
        _embed_one(client, "http://ollama", "model", "Odin")


def test_valid_embedding_is_preserved():
    transport = httpx.MockTransport(lambda request: httpx.Response(200, json={"embeddings": [[1, 2]]}))
    with httpx.Client(transport=transport) as client:
        np.testing.assert_array_equal(_embed_one(client, "http://ollama", "model", "Odin"), [1, 2])


def test_known_names_match_lowercase_and_unicode_without_partial_words():
    vocab = {"odin": "Odin", "þórr": "Þórr", "sif gold hair": "Sif Gold Hair"}
    assert extract_candidates("odin and þórr met sif\tgold hair; odinsbeard stayed.", vocab) == [
        "Odin", "Þórr", "Sif Gold Hair"]


def test_empty_vocabulary_uses_open_mode():
    assert extract_candidates("Odin spoke", {}) == ["Odin"]
