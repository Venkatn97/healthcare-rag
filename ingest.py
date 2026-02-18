import fitz
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone, ServerlessSpec
from config import PINECONE_API_KEY, CLIENT_CONFIG

pc = Pinecone(api_key=PINECONE_API_KEY)
model = SentenceTransformer("BAAI/bge-base-en-v1.5")  # better for medical text

INDEX_NAME = "healthcare-rag"

def setup_index():
    if INDEX_NAME not in pc.list_indexes().names():
        pc.create_index(
            name=INDEX_NAME,
            dimension=768,  # BGE base outputs 768 dims
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    return pc.Index(INDEX_NAME)

def extract_text_by_page(pdf_path):
    doc = fitz.open(pdf_path)
    pages = []
    for i, page in enumerate(doc):
        pages.append({"text": page.get_text(), "page": i + 1})
    return pages

def chunk_text(text, chunk_size=400, overlap=80):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunk = " ".join(words[i:i + chunk_size])
        if chunk:
            chunks.append(chunk)
    return chunks

def ingest(pdf_path, doc_name="document"):
    index = setup_index()
    pages = extract_text_by_page(pdf_path)

    vectors = []
    chunk_id = 0

    for page_data in pages:
        chunks = chunk_text(page_data["text"])
        embeddings = model.encode(chunks).tolist()

        for i, chunk in enumerate(chunks):
            vectors.append({
                "id": f"{doc_name}-chunk-{chunk_id}",
                "values": embeddings[i],
                "metadata": {
                    "text": chunk,
                    "page": page_data["page"],
                    "source": doc_name
                }
            })
            chunk_id += 1

    # upsert in batches of 100
    for i in range(0, len(vectors), 100):
        index.upsert(
            vectors=vectors[i:i+100],
            namespace=CLIENT_CONFIG["namespace"]
        )

    print(f"Ingested {chunk_id} chunks from {doc_name}")

if __name__ == "__main__":
    print("Use the Streamlit app to upload documents")
