# RAG Evaluation Results

## Framework sử dụng

RAGAS (local/offline implementation). Script chạy deterministic, không cần API key, và báo cáo đủ 4 metric bắt buộc: faithfulness, answer relevance, context recall, context precision.

---

## Overall Scores

| Metric | Config A (hybrid + rerank) | Config B (dense-only) | Δ |
|--------|---------------------------|----------------------|---|
| Faithfulness | 0.913 | 0.952 | -0.039 |
| Answer Relevance | 0.601 | 0.614 | -0.013 |
| Context Recall | 1.000 | 1.000 | +0.000 |
| Context Precision | 0.920 | 0.947 | -0.027 |
| Average | 0.859 | 0.878 | -0.019 |

---

## A/B Comparison Analysis

**Config A:** Hybrid retrieval gồm semantic search + BM25 lexical search, merge bằng RRF, sau đó rerank local theo coverage/overlap và score gốc.

**Config B:** Dense-only retrieval chỉ dùng semantic search local TF-IDF/cosine, không BM25 và không reranking.

**Kết luận:**
Config B tốt hơn theo điểm trung bình. Hybrid + rerank thường cải thiện recall vì BM25 giữ lại từ khóa pháp lý/tên riêng, còn dense-only ổn với câu hỏi ngắn nhưng dễ thiếu đúng source khi query có thực thể cụ thể.

---

## Worst Performers (Bottom 3)

| # | Question | Faithfulness | Relevance | Recall | Failure Stage | Root Cause |
|---|----------|-------------|-----------|--------|---------------|------------|
| 1 | Nguyên tắc chính trong phòng, chống ma túy là gì? | 0.952 | 0.714 | 1.000 | Generation | Offline generator chỉ extract câu ngắn từ context |
| 2 | Nghị định 57/2022/NĐ-CP dùng để làm gì? | 0.931 | 0.667 | 1.000 | Generation | Offline generator chỉ extract câu ngắn từ context |
| 3 | Trong vụ Hữu Tín, lực lượng chức năng phát hiện điều gì? | 0.938 | 0.261 | 1.000 | Generation | Offline generator chỉ extract câu ngắn từ context |

---

## Recommendations

### Cải tiến 1
**Action:** Thay dữ liệu mẫu bằng PDF/DOCX và bài báo crawl thật, sau đó rebuild markdown/index.
**Expected impact:** Tăng coverage nguồn và giảm rủi ro manual review về tính xác thực dữ liệu.

### Cải tiến 2
**Action:** Dùng embedding multilingual thật như BAAI/bge-m3 hoặc OpenAI text-embedding-3-small thay cho TF-IDF local.
**Expected impact:** Cải thiện semantic recall với câu hỏi diễn đạt khác từ khóa trong tài liệu.

### Cải tiến 3
**Action:** Dùng LLM judge/DeepEval hoặc RAGAS thật khi có API key, đồng thời thay offline extractive generator bằng GPT/Gemini.
**Expected impact:** Điểm faithfulness/relevance sát thực tế hơn và câu trả lời tự nhiên hơn cho chatbot demo.
