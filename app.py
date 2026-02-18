import streamlit as st
import tempfile
import os
from ingest import ingest
from query import answer
from feedback import log_feedback

st.set_page_config(page_title="Healthcare Document Q&A", page_icon="🏥", layout="wide")

st.title("🏥 Healthcare Document Intelligence")
st.caption("Upload clinical guidelines or SOPs and query them using natural language")

# Initialize session state
if "indexed_file" not in st.session_state:
    st.session_state["indexed_file"] = None
if "question" not in st.session_state:
    st.session_state["question"] = ""

# Layout
col1, col2 = st.columns([1, 2])

# Left column - Upload
with col1:
    st.subheader("Upload Document")
    st.caption("Drag and drop your PDF here")

    uploaded_file = st.file_uploader(
        label="Upload PDF",
        type=["pdf"],
        label_visibility="collapsed"
    )

    if uploaded_file:
        st.info(f"**{uploaded_file.name}**")
        st.caption(f"Size: {round(uploaded_file.size / 1024, 1)} KB")

        if st.button("⚡ Index Document", use_container_width=True):
            if st.session_state["indexed_file"] != uploaded_file.name:
                with st.spinner("Indexing document into Pinecone..."):
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                        tmp.write(uploaded_file.read())
                        tmp_path = tmp.name
                    ingest(tmp_path, doc_name=uploaded_file.name)
                    os.unlink(tmp_path)
                st.session_state["indexed_file"] = uploaded_file.name
                st.success("Document indexed! You can now ask questions.")
            else:
                st.warning("Already indexed! Go ahead and ask questions.")

# Right column - Q&A
with col2:
    st.subheader("💬 Ask a Question")

    # Example questions
    st.caption("Try asking:")
    example_questions = [
        "What is the patient handoff protocol?",
        "What are the infection control guidelines?",
        "What are the emergency procedures?"
    ]

    for q in example_questions:
        if st.button(q, use_container_width=True):
            st.session_state["question"] = q

    question = st.text_input(
        "Your question:",
        value=st.session_state.get("question", ""),
        placeholder="Type your question here..."
    )

    if st.button("🔍 Ask", use_container_width=True) and question:
        if st.session_state["indexed_file"] is None:
            st.error("Please upload and index a document first!")
        else:
            with st.spinner("Searching guidelines..."):
                result = answer(question)

            st.subheader("Answer")
            st.write(result["answer"])

            if result["sources"]:
                st.subheader("Sources")
                for source in result["sources"]:
                    st.caption(f" {source}")

            # Feedback
            st.divider()
            st.write("Was this helpful?")
            col_a, col_b = st.columns(2)
            with col_a:
                if st.button(" Yes", use_container_width=True):
                    log_feedback(question, result["answer"], "good")
                    st.success("Thanks!")
            with col_b:
                if st.button(" No", use_container_width=True):
                    log_feedback(question, result["answer"], "bad")
                    st.warning("Logged — we'll improve this.")