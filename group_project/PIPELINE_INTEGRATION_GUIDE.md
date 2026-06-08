# Pipeline Integration Guide

File này hướng dẫn thành viên nhóm thêm pipeline cá nhân vào app nhóm và chạy demo/evaluation.

## Ý Nghĩa

"Tích hợp pipeline từ bài cá nhân của các thành viên" nghĩa là mỗi thành viên expose pipeline RAG của mình qua cùng một interface để app nhóm có thể gọi thống nhất.

Hiện app nhóm dùng [pipeline_registry.py](pipeline_registry.py) làm nơi đăng ký pipeline. Streamlit app ở [`../app.py`](../app.py) đọc registry này và cho chọn pipeline ở sidebar.

## Yêu Cầu Interface

Mỗi pipeline cần có 2 hàm:

```python
def answer(query: str, top_k: int = 5) -> dict:
    return {
        "answer": "Câu trả lời có citation [Nguồn, Năm]",
        "sources": [
            {
                "content": "Nội dung chunk",
                "score": 0.83,
                "metadata": {
                    "source": "ten-file.md",
                    "type": "legal",
                    "chunk_index": 0,
                },
                "source": "hybrid",
            }
        ],
    }


def search(query: str, top_k: int = 5) -> list[dict]:
    return [
        {
            "content": "Nội dung chunk",
            "score": 0.83,
            "metadata": {"source": "ten-file.md", "type": "legal"},
            "source": "hybrid",
        }
    ]
```

Các key bắt buộc để UI hiển thị đẹp:

| Key | Bắt buộc | Mô tả |
|---|---:|---|
| `answer` | Có | Chuỗi câu trả lời có citation |
| `sources` | Có | Danh sách source chunks đã dùng |
| `content` | Có | Nội dung chunk |
| `score` | Có | Điểm relevance, kiểu float |
| `metadata.source` | Nên có | Tên file hoặc nguồn |
| `metadata.type` | Nên có | `legal`, `news`, hoặc loại tài liệu |
| `source` | Nên có | Retrieval route, ví dụ `hybrid`, `pageindex`, `dense` |

## Cách Thêm Pipeline Mới

Ví dụ thành viên `MemberA` có module:

```text
src/member_a_pipeline.py
```

và trong đó có:

```python
def generate_with_citation(query: str, top_k: int = 5) -> dict:
    ...


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    ...
```

Thêm adapter vào [pipeline_registry.py](pipeline_registry.py):

```python
from src.member_a_pipeline import (
    generate_with_citation as member_a_generate,
    retrieve as member_a_retrieve,
)


def _member_a_answer(query: str, top_k: int = 5) -> dict:
    return member_a_generate(query, top_k=top_k)


def _member_a_retrieve(query: str, top_k: int = 5) -> list[dict]:
    return member_a_retrieve(query, top_k=top_k)
```

Sau đó thêm entry vào `PIPELINES`:

```python
PIPELINES = {
    "namlh_local_rag": PipelineAdapter(...),
    "member_a_rag": PipelineAdapter(
        key="member_a_rag",
        owner="MemberA - MSSV",
        description="Short description of MemberA retrieval/generation pipeline.",
        answer_fn=_member_a_answer,
        retrieve_fn=_member_a_retrieve,
    ),
}
```

Sau khi thêm, chạy Streamlit app và chọn pipeline mới ở sidebar.

## Cách Chạy

Kích hoạt venv:

```bash
source /home/namle/VINAI/.venv/bin/activate
```

Cài dependencies nếu thiếu:

```bash
pip install -r requirements.txt
```

Chạy test bài cá nhân:

```bash
pytest tests/test_individual.py -q
```

Chạy chatbot/search demo:

```bash
streamlit run app.py --server.headless true --server.port 8501
```

Mở:

```text
http://localhost:8501
```

Chạy evaluation và xuất lại báo cáo:

```bash
python group_project/evaluation/eval_pipeline.py
```

Kết quả nằm ở:

```text
group_project/evaluation/results.md
```

## Test Nhanh Adapter

Sau khi đăng ký pipeline mới, chạy:

```bash
python - <<'PY'
from group_project.pipeline_registry import list_pipelines, get_pipeline

for pipeline in list_pipelines():
    print(pipeline.key, pipeline.owner)
    result = pipeline.answer("Luật Phòng chống ma túy quy định gì về cai nghiện?", top_k=3)
    print(result["answer"][:300])
    print("sources:", len(result.get("sources", [])))
PY
```

Nếu output có answer và sources, pipeline đã tích hợp được với app.

## Checklist Cho Thành Viên

- [ ] Pipeline cá nhân chạy được độc lập.
- [ ] `answer(query, top_k)` trả về dict có `answer` và `sources`.
- [ ] `search(query, top_k)` trả về list chunks có `content`, `score`, `metadata`.
- [ ] Thêm adapter vào `group_project/pipeline_registry.py`.
- [ ] Chạy test adapter nhanh.
- [ ] Chạy `streamlit run app.py` và chọn pipeline ở sidebar.
- [ ] Chạy `python group_project/evaluation/eval_pipeline.py` nếu pipeline được dùng cho evaluation.

## Lưu Ý Khi Merge Code Nhóm

- Không đổi signature của `PipelineAdapter`.
- Không đổi format `answer` / `sources` nếu chưa cập nhật app.
- Nếu pipeline cần API key, đọc từ `.env` và fallback rõ ràng khi thiếu key.
- Nếu thành viên dùng vector store riêng, giữ code khởi tạo trong module của thành viên, không hard-code vào app.
- Nếu muốn evaluation so sánh pipeline của nhiều thành viên, cập nhật `group_project/evaluation/eval_pipeline.py` để gọi key pipeline tương ứng từ registry.
