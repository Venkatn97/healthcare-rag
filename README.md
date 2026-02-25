# 🏥 Healthcare Document Intelligence System

A Retrieval-Augmented Generation (RAG) system that lets healthcare staff query clinical guidelines, SOPs, and medical documents using natural language — powered by **Pinecone**, **Claude AI**, and **Streamlit**.

---

## 🎯 What It Does

Instead of manually searching through hundreds of pages of medical documents, staff simply upload a PDF and ask questions in plain English. The system finds the most relevant sections and generates a clear, grounded answer.

```
Upload PDF → Index into Pinecone → Ask a question → Get an answer with sources
```

---

## 🖥️ Demo

![App Screenshot](assets/demo.png)

> *"What is the infection control protocol for patient isolation?"*
> The system retrieves the relevant section from the uploaded SOP and generates a concise answer with page references.

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|-----------|
| Vector Database | Pinecone |
| Embeddings | BAAI/bge-base-en-v1.5 (Hugging Face) |
| LLM | Claude Haiku (Anthropic) |
| PDF Parsing | PyMuPDF |
| Frontend | Streamlit |
| Language | Python 3.11 |

---

## 🏗️ Architecture

```
PDF Upload (Streamlit UI)
    ↓
Text Extraction (PyMuPDF)
    ↓
Chunking (400 words, 80 overlap)
    ↓
Embedding (BGE base model)
    ↓
Vector Storage (Pinecone - namespace per client)
    ↓
User Question → Embed → Similarity Search → Top 4 Chunks
    ↓
Claude Haiku generates answer with source attribution
```

---

## 📁 Project Structure

```
healthcare-rag/
├── app.py            # Streamlit UI - drag and drop upload + Q&A
├── ingest.py         # PDF parsing, chunking, embedding, Pinecone upsert
├── query.py          # Retrieval + Claude answer generation
├── feedback.py       # Logs good/bad answers for iteration
├── config.py         # API keys, client config, prompt template
├── .env              # API keys (never committed)
├── .gitignore
└── requirements.txt
```

---

## 🚀 Getting Started

### 1. Clone the repo
```bash
git clone https://github.com/YOUR_USERNAME/healthcare-rag.git
cd healthcare-rag
```

### 2. Install dependencies
```bash
pip install pinecone anthropic sentence-transformers pymupdf streamlit python-dotenv
```

### 3. Set up environment variables
Create a `.env` file in the root directory:
```bash
PINECONE_API_KEY=your_pinecone_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

Get your keys:
- Pinecone: [app.pinecone.io](https://app.pinecone.io)
- Anthropic: [console.anthropic.com](https://console.anthropic.com)

### 4. Run the app
```bash
streamlit run app.py
```

### 5. Use the app
1. Drag and drop any healthcare PDF into the upload area
2. Click **Index Document**
3. Ask questions about the document
4. Rate answers to help improve the system

---

## ✨ Key Features

**Multi-document support** — Upload and query different documents. Each is tracked separately.

**Source attribution** — Every answer shows which page and document it came from so staff can verify information.

**Safety-first prompt** — Claude never fabricates medical information. If the answer is not in the document it says so explicitly.

**Feedback logging** — Staff can rate answers as helpful or not. Logs are saved to `feedback_log.json` for iteration.

**Client namespace isolation** — Each client's data is stored in a separate Pinecone namespace so data never mixes.

---

## 🔧 Configuration

Edit `config.py` to customize per client:

```python
CLIENT_CONFIG = {
    "namespace": "hospital_A",       # change per client
    "prompt": "You are a clinical assistant..."  # customize tone and rules
}
```

---

## 📊 How It Works — RAG Pipeline

**Ingestion**
- PDF text is extracted page by page using PyMuPDF
- Text is split into 400-word chunks with 80-word overlap to preserve context
- Each chunk is converted to a 768-dimensional vector using BGE embeddings
- Vectors are stored in Pinecone with metadata (text, page number, source filename)

**Retrieval**
- User's question is converted to a vector using the same embedding model
- Pinecone performs cosine similarity search and returns top 4 most relevant chunks
- Chunks are filtered by client namespace to ensure data isolation

**Generation**
- Retrieved chunks are passed to Claude Haiku as context
- Claude generates a grounded answer using only the provided context
- Answer is returned alongside source references (document name + page number)

---

## 🏥 Use Case — Forward Deployed Context

This system was built to simulate a real Forward Deployed Engineering scenario:

- **Client:** Hospital network with 200+ page SOPs staff rarely read
- **Problem:** Staff waste time searching documents manually during critical moments
- **Solution:** Deploy this system on-site, upload their documents, staff query instantly
- **Time to value:** Under 10 minutes from deployment to first query

---

## 🔮 Future Improvements

- [ ] Multi-file querying across all uploaded documents simultaneously
- [ ] Role-based access control (doctors vs nurses see different documents)
- [ ] Usage analytics dashboard (most asked questions, peak usage times)
- [ ] Docker containerization for faster on-site deployment
- [ ] Support for Word (.docx) and Excel (.xlsx) documents
- [ ] Automated re-indexing when documents are updated

---

## 📄 License

MIT License — free to use and modify.

---
