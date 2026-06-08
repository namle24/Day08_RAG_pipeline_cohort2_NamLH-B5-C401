"""Task 5 — Semantic Search Module."""

from collections import Counter

from .local_retrieval import corpus_idf, cosine_from_counters, expanded_tokens, get_chunks


def semantic_search(query: str, top_k: int = 10) -> list[dict]:
    """
    Tìm kiếm ngữ nghĩa sử dụng vector similarity.

    Args:
        query: Câu truy vấn
        top_k: Số lượng kết quả tối đa

    Returns:
        List of {
            'content': str,      # Nội dung chunk
            'score': float,      # Cosine similarity score
            'metadata': dict     # source, doc_type, chunk_index
        }
        Sorted by score descending.
    """
    chunks = list(get_chunks())
    if not chunks or top_k <= 0:
        return []

    corpus_tokens = [expanded_tokens(chunk["content"]) for chunk in chunks]
    idf = corpus_idf(corpus_tokens)
    query_vector = Counter(expanded_tokens(query))

    results = []
    for chunk, tokens in zip(chunks, corpus_tokens):
        score = cosine_from_counters(query_vector, Counter(tokens), idf)
        if score > 0:
            results.append({
                "content": chunk["content"],
                "score": float(score),
                "metadata": dict(chunk.get("metadata", {})),
            })

    results.sort(key=lambda item: item["score"], reverse=True)
    return results[:top_k]


if __name__ == "__main__":
    # Test
    results = semantic_search("hình phạt cho tội tàng trữ ma tuý", top_k=5)
    for r in results:
        print(f"[{r['score']:.3f}] {r['content'][:100]}...")
