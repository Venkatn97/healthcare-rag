import anthropic
from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
from config import PINECONE_API_KEY, ANTHROPIC_API_KEY, CLIENT_CONFIG

pc = Pinecone(api_key=PINECONE_API_KEY)
model = SentenceTransformer("BAAI/bge-base-en-v1.5")
client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

def get_index():
    return pc.Index("healthcare-rag")  # connects only when called

def retrieve(question, top_k=4):
    index = get_index()  # get index here not at startup
    query_vec = model.encode(question).tolist()
    results = index.query(
        vector=query_vec,
        top_k=top_k,
        include_metadata=True,
        namespace=CLIENT_CONFIG["namespace"]
    )
    return [
        {
            "text": m["metadata"]["text"],
            "page": m["metadata"].get("page", "N/A"),
            "source": m["metadata"].get("source", "N/A"),
            "score": round(m["score"], 3)
        }
        for m in results["matches"]
    ]

def answer(question):
    chunks = retrieve(question)
    context = "\n\n".join([c["text"] for c in chunks])
    sources = list(set([f"{c['source']} (Page {c['page']})" for c in chunks]))

    prompt = f"""{CLIENT_CONFIG["prompt"]}

Context:
{context}

Question: {question}

Answer:"""

    response = client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}]
    )

    return {
        "answer": response.content[0].text,
        "sources": sources,
        "chunks_used": len(chunks)
    }