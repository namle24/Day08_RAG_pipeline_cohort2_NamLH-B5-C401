# Bài Tập Nhóm — Search Engine / RAG Chatbot

## Mục Tiêu

Sau khi hoàn thành bài cá nhân, nhóm ngồi lại để xây dựng **1 trong 2 sản phẩm**:

---

## Yêu cầu 1:  Sản phẩm nhóm RAG Chatbot

Xây dựng chatbot trả lời câu hỏi về pháp luật ma tuý và tin tức liên quan.

**Yêu cầu:**
- Giao diện chat (Streamlit / Gradio / Chainlit)
- Trả lời có citation (dựa trên Task 10)
- Hỗ trợ follow-up questions (conversation memory)
- Hiển thị source documents đã dùng

**Stack gợi ý:**
```
Chainlit/Streamlit → Retrieval (Task 9) → Generation (Task 10) → Display
```

---

## Yêu cầu 2: RAG Evaluation Pipeline

Sử dụng **1 trong 3 framework** sau để evaluate pipeline RAG của nhóm:

### Framework lựa chọn

| Framework | Cài đặt | Đặc điểm |
|-----------|---------|-----------|
| [DeepEval](https://github.com/confident-ai/deepeval) | `pip install deepeval` | Nhiều metric built-in, dễ integrate với pytest |
| [RAGAS](https://github.com/explodinggradients/ragas) | `pip install ragas` | Chuẩn industry cho RAG eval, 3 trục chính |
| [TruLens](https://github.com/truera/trulens) | `pip install trulens` | Dashboard UI, feedback functions mạnh |

### Yêu cầu Evaluation

1. **Tạo Golden Dataset** — tối thiểu 15 cặp Q&A (question, expected_answer, expected_context)
2. **Chạy evaluation** trên toàn bộ golden dataset với các metrics sau:
   - **Faithfulness** — câu trả lời có bám đúng context không?
   - **Answer Relevance** — câu trả lời có đúng câu hỏi không?
   - **Context Recall** — retriever có lấy đủ evidence không?
   - **Context Precision** — trong context lấy về, bao nhiêu % thực sự hữu ích?
3. **So sánh A/B** — chạy eval trên ít nhất 2 config khác nhau (ví dụ: có reranking vs không reranking, hoặc hybrid vs dense-only)
4. **Báo cáo** — bảng điểm + phân tích worst performers + đề xuất cải tiến

### Code mẫu — DeepEval

```python
from deepeval import evaluate
from deepeval.metrics import (
    FaithfulnessMetric,
    AnswerRelevancyMetric,
    ContextualRecallMetric,
    ContextualPrecisionMetric,
)
from deepeval.test_case import LLMTestCase

# Tạo test cases từ golden dataset
test_cases = []
for item in golden_dataset:
    result = rag_pipeline.generate_with_citation(item["question"])
    test_case = LLMTestCase(
        input=item["question"],
        actual_output=result["answer"],
        expected_output=item["expected_answer"],
        retrieval_context=[c["content"] for c in result["sources"]],
    )
    test_cases.append(test_case)

# Chạy evaluation
metrics = [
    FaithfulnessMetric(threshold=0.7),
    AnswerRelevancyMetric(threshold=0.7),
    ContextualRecallMetric(threshold=0.7),
    ContextualPrecisionMetric(threshold=0.7),
]

results = evaluate(test_cases, metrics)
```

### Code mẫu — RAGAS

```python
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_recall,
    context_precision,
)
from datasets import Dataset

# Chuẩn bị data
eval_data = {
    "question": [],
    "answer": [],
    "contexts": [],
    "ground_truth": [],
}

for item in golden_dataset:
    result = rag_pipeline.generate_with_citation(item["question"])
    eval_data["question"].append(item["question"])
    eval_data["answer"].append(result["answer"])
    eval_data["contexts"].append([c["content"] for c in result["sources"]])
    eval_data["ground_truth"].append(item["expected_answer"])

dataset = Dataset.from_dict(eval_data)

# Chạy evaluation
result = evaluate(
    dataset,
    metrics=[faithfulness, answer_relevancy, context_recall, context_precision],
)
print(result.to_pandas())
```

### Code mẫu — TruLens

```python
from trulens.apps.custom import TruCustomApp, instrument
from trulens.core import Feedback
from trulens.providers.openai import OpenAI as TruOpenAI

provider = TruOpenAI()

# Define feedback functions
f_faithfulness = Feedback(provider.groundedness_measure_with_cot_reasons).on_output()
f_relevance = Feedback(provider.relevance).on_input_output()
f_context_relevance = Feedback(provider.context_relevance).on_input()

# Wrap RAG pipeline
tru_rag = TruCustomApp(
    rag_pipeline,
    app_name="DrugLaw_RAG",
    feedbacks=[f_faithfulness, f_relevance, f_context_relevance],
)

# Run evaluation
with tru_rag as recording:
    for item in golden_dataset:
        rag_pipeline.generate_with_citation(item["question"])

# View dashboard
from trulens.dashboard import run_dashboard
run_dashboard()
```

### Deliverable Evaluation

- [ ] File `group_project/evaluation/golden_dataset.json` — 15+ cặp Q&A
- [ ] File `group_project/evaluation/eval_pipeline.py` — script chạy evaluation
- [ ] File `group_project/evaluation/results.md` — bảng điểm + phân tích
- [ ] So sánh A/B ít nhất 2 configs

---

## Yêu Cầu Chung

1. **Tích hợp pipeline** từ bài cá nhân của các thành viên
2. **Demo hoạt động được** trong buổi trình bày (chạy local hoặc deploy)
3. **Evaluation pipeline** chạy được và có báo cáo kết quả
4. **Code push lên repository** chung của nhóm
5. **README** mô tả kiến trúc và phân công (điền bên dưới)

---

## Kiến Trúc Hệ Thống

```
Member pipelines
        │
        ├── NamLH local RAG pipeline
        │       ├── Task 3 Convert Markdown → data/standardized
        │       ├── Task 4 Chunking + Local JSON Index
        │       ├── Task 5 Semantic Search
        │       ├── Task 6 BM25 Lexical Search
        │       ├── Task 9 Hybrid Retrieval: RRF + rerank + PageIndex fallback
        │       └── Task 10 Generation with citation
        │
        └── Future member adapters
                └── group_project/pipeline_registry.py

group_project/pipeline_registry.py
        │
        ▼
Streamlit app.py
        ├── Chat UI with conversation memory
        ├── Search UI with score/source display
        └── Evaluation report tab

Evaluation
        │
        ▼
group_project/evaluation/eval_pipeline.py
        ├── Golden dataset 15 Q&A
        ├── Config A: hybrid + rerank
        └── Config B: dense-only
```

---

## Phân Công Công Việc

| Thành viên | MSSV | Nhiệm vụ | Trạng thái |
|-----------|------|----------|------------|
| NamLH | B5-C401 | Cá nhân Task 1-10: data, convert, chunk/index, retrieval, generation citation | Hoàn thành |
|  | B5-C401 | Tích hợp pipeline cá nhân vào `group_project/pipeline_registry.py` | Hoàn thành |
|  | B5-C401 | Streamlit chatbot/search UI, source display, conversation memory | Hoàn thành |
|  | B5-C401 | Golden dataset 15 Q&A cho evaluation | Hoàn thành |
|  | B5-C401 | Evaluation pipeline A/B và báo cáo `results.md` | Hoàn thành |
| Thành viên khác | TBD | Bổ sung adapter pipeline riêng nếu có | Chờ tích hợp |

---

## Hướng Dẫn Chạy

```bash
# Cài đặt dependencies
pip install -r requirements.txt

# Chạy test bài cá nhân
pytest tests/test_individual.py -q

# Rebuild dữ liệu mẫu/index local nếu cần
python -m src.bootstrap_sample_data

# Chạy evaluation nhóm và xuất results.md
python group_project/evaluation/eval_pipeline.py

# Chạy chatbot/search demo
streamlit run app.py
```

## Tích Hợp Pipeline Thành Viên

Trong repo nhóm, "tích hợp pipeline từ bài cá nhân của các thành viên" nghĩa là mỗi thành viên expose pipeline của mình qua cùng một interface:

- `answer(query, top_k)` trả về `{"answer": str, "sources": list[dict]}`
- `search(query, top_k)` trả về list source chunks có `content`, `score`, `metadata`

File `group_project/pipeline_registry.py` là nơi đăng ký các adapter đó. Hiện app đã tích hợp pipeline của NamLH (`namlh_local_rag`). Khi thành viên khác có pipeline riêng, chỉ cần thêm adapter mới vào `PIPELINES`, Streamlit app sẽ có thể chọn pipeline đó từ sidebar.

Hướng dẫn chi tiết cho thành viên nhóm: [PIPELINE_INTEGRATION_GUIDE.md](PIPELINE_INTEGRATION_GUIDE.md).

---

## Lưu ý: Hãy giữ lại repo này nếu như bạn học track 3 giai đoạn 2, chúng ta sẽ phát triển tiếp dự án lên knowledge graph để khắc phục các câu hỏi hóc búa khi có các câu hỏi khó.
