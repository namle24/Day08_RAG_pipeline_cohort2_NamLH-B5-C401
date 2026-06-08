"""
Registry for integrating individual member RAG pipelines into the group app.

In a real group repository, each member can add one adapter here that exposes
the same answer/retrieve interface. The Streamlit app and evaluation pipeline
can then run against any registered member pipeline without changing UI code.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from src.task10_generation import generate_with_citation
from src.task9_retrieval_pipeline import retrieve


@dataclass(frozen=True)
class PipelineAdapter:
    key: str
    owner: str
    description: str
    answer_fn: Callable[[str, int], dict]
    retrieve_fn: Callable[[str, int], list[dict]]

    def answer(self, query: str, top_k: int = 5) -> dict:
        return self.answer_fn(query, top_k)

    def search(self, query: str, top_k: int = 5) -> list[dict]:
        return self.retrieve_fn(query, top_k)


def _namlh_answer(query: str, top_k: int = 5) -> dict:
    return generate_with_citation(query, top_k=top_k)


def _namlh_retrieve(query: str, top_k: int = 5) -> list[dict]:
    return retrieve(query, top_k=top_k)


PIPELINES = {
    "namlh_local_rag": PipelineAdapter(
        key="namlh_local_rag",
        owner="NamLH - B5-C401",
        description=(
            "Hybrid local RAG: semantic TF-IDF/cosine + BM25, RRF merge, "
            "local reranking, PageIndex-style fallback, citation generation."
        ),
        answer_fn=_namlh_answer,
        retrieve_fn=_namlh_retrieve,
    ),
}


def list_pipelines() -> list[PipelineAdapter]:
    return list(PIPELINES.values())


def get_pipeline(key: str) -> PipelineAdapter:
    if key not in PIPELINES:
        raise KeyError(f"Unknown pipeline: {key}")
    return PIPELINES[key]
