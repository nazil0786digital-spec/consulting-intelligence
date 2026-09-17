import hashlib
import math
import os
import re
from typing import Protocol


# Match text-embedding-3-small's default dimensions so the local fallback and
# PostgreSQL vector column share one storage contract.
LOCAL_VECTOR_DIMENSIONS = 1536


class EmbeddingProvider(Protocol):
    name: str

    def embed(self, text: str) -> list[float]: ...


class DeterministicEmbeddingProvider:
    """Offline development fallback; not a substitute for production semantic embeddings."""

    name = "deterministic-local"

    def embed(self, text: str) -> list[float]:
        vector = [0.0] * LOCAL_VECTOR_DIMENSIONS
        for term in re.findall(r"[a-z0-9]+", text.lower()):
            digest = hashlib.sha256(term.encode("utf-8")).digest()
            index = int.from_bytes(digest[:4], "big") % LOCAL_VECTOR_DIMENSIONS
            vector[index] += 1.0 if digest[4] % 2 else -1.0
        return normalize(vector)


class OpenAIEmbeddingProvider:
    name = "openai"

    def __init__(self, api_key: str, model: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)
        self.model = model

    def embed(self, text: str) -> list[float]:
        response = self.client.embeddings.create(model=self.model, input=text)
        return response.data[0].embedding


def get_embedding_provider() -> EmbeddingProvider:
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        return OpenAIEmbeddingProvider(api_key=api_key, model=os.getenv("EMBEDDING_MODEL", "text-embedding-3-small"))
    return DeterministicEmbeddingProvider()


def normalize(vector: list[float]) -> list[float]:
    magnitude = math.sqrt(sum(value * value for value in vector))
    return [value / magnitude for value in vector] if magnitude else vector


def cosine_similarity(left: list[float], right: list[float]) -> float:
    if len(left) != len(right):
        raise ValueError("Embedding vectors must use the same dimensions.")
    return sum(left_value * right_value for left_value, right_value in zip(left, right, strict=True))
