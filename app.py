from __future__ import annotations

import sys
from html import escape
from pathlib import Path

import streamlit as st


PROJECT_DIR = Path(__file__).resolve().parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

from group_project.pipeline_registry import get_pipeline, list_pipelines


RESULTS_PATH = PROJECT_DIR / "group_project" / "evaluation" / "results.md"


st.set_page_config(
    page_title="DrugLaw RAG",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --surface: #f7f8fa;
        --line: #d6dae1;
        --ink: #171b22;
        --muted: #5d6673;
        --accent: #0f766e;
    }
    .stApp {
        background: var(--surface);
        color: var(--ink);
    }
    .block-container {
        padding-top: 1.25rem;
        padding-bottom: 2rem;
        max-width: 1280px;
    }
    h1, h2, h3 {
        letter-spacing: 0;
    }
    .rag-title {
        font-size: 1.55rem;
        font-weight: 720;
        margin: 0 0 .15rem 0;
    }
    .rag-subtitle {
        color: var(--muted);
        font-size: .94rem;
        margin-bottom: 1rem;
    }
    .source-row {
        border: 1px solid var(--line);
        border-radius: 6px;
        padding: .75rem .85rem;
        margin-bottom: .55rem;
        background: #ffffff;
    }
    .source-meta {
        color: var(--muted);
        font-size: .82rem;
        margin-bottom: .35rem;
    }
    .source-content {
        font-size: .91rem;
        line-height: 1.45;
    }
    .metric-box {
        border: 1px solid var(--line);
        border-radius: 6px;
        background: #ffffff;
        padding: .8rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _init_state() -> None:
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("last_sources", [])


def _source_label(source: dict, idx: int) -> str:
    metadata = source.get("metadata", {})
    name = metadata.get("source") or metadata.get("path") or f"Source {idx}"
    retrieval = source.get("source", "hybrid")
    score = source.get("score", 0.0)
    return f"{idx}. {name} | {retrieval} | score={score:.3f}"


def _render_sources(sources: list[dict]) -> None:
    if not sources:
        st.info("No source documents returned.")
        return

    for idx, source in enumerate(sources, 1):
        metadata = source.get("metadata", {})
        source_type = metadata.get("type", "unknown")
        chunk_index = metadata.get("chunk_index", "n/a")
        label = _source_label(source, idx)
        snippet = escape(source.get("content", "").replace("\n", " ").strip())
        label = escape(label)
        source_type = escape(str(source_type))
        chunk_index = escape(str(chunk_index))
        if len(snippet) > 900:
            snippet = snippet[:900] + "..."
        st.markdown(
            f"""
            <div class="source-row">
                <div class="source-meta">{label} | type={source_type} | chunk={chunk_index}</div>
                <div class="source-content">{snippet}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )


def _conversation_query(user_input: str) -> str:
    previous_user_messages = [
        item["content"]
        for item in st.session_state.messages
        if item.get("role") == "user"
    ][-2:]
    if not previous_user_messages:
        return user_input
    history = " | ".join(previous_user_messages)
    return f"Ngữ cảnh hội thoại gần nhất: {history}. Câu hỏi hiện tại: {user_input}"


def main() -> None:
    _init_state()

    pipelines = list_pipelines()
    pipeline_options = {f"{p.owner} ({p.key})": p.key for p in pipelines}

    with st.sidebar:
        st.markdown("### Pipeline")
        selected_label = st.selectbox("Member pipeline", list(pipeline_options.keys()))
        top_k = st.slider("Top K", min_value=3, max_value=10, value=5, step=1)
        use_memory = st.toggle("Conversation memory", value=True)
        pipeline = get_pipeline(pipeline_options[selected_label])
        st.caption(pipeline.description)
        if st.button("Clear chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.last_sources = []
            st.rerun()

    st.markdown('<div class="rag-title">DrugLaw RAG Chatbot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="rag-subtitle">Chatbot tra cứu pháp luật ma túy và tin tức nghệ sĩ liên quan, có citation và source documents.</div>',
        unsafe_allow_html=True,
    )

    chat_tab, search_tab, eval_tab = st.tabs(["Chat", "Search", "Evaluation"])

    with chat_tab:
        chat_col, source_col = st.columns([0.62, 0.38], gap="large")

        with chat_col:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            prompt = st.chat_input("Hỏi về luật phòng chống ma túy hoặc tin tức liên quan")
            if prompt:
                st.session_state.messages.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                query = _conversation_query(prompt) if use_memory else prompt
                with st.chat_message("assistant"):
                    with st.spinner("Retrieving and generating answer..."):
                        result = pipeline.answer(query, top_k=top_k)
                    answer = result.get("answer", "")
                    st.markdown(answer)

                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.session_state.last_sources = result.get("sources", [])

        with source_col:
            st.markdown("### Sources")
            _render_sources(st.session_state.last_sources)

    with search_tab:
        query = st.text_input("Search query", value="Luật Phòng chống ma túy quy định gì về cai nghiện?")
        if st.button("Run search", type="primary"):
            with st.spinner("Searching..."):
                results = pipeline.search(query, top_k=top_k)
            st.session_state.search_results = results

        _render_sources(st.session_state.get("search_results", []))

    with eval_tab:
        st.markdown("### Evaluation Report")
        if RESULTS_PATH.exists():
            st.markdown(RESULTS_PATH.read_text(encoding="utf-8"))
        else:
            st.warning("Evaluation report not found. Run `python group_project/evaluation/eval_pipeline.py`.")


if __name__ == "__main__":
    main()
