# rag_backend.py
from typing import List, Tuple
import chromadb
from openai import OpenAI

CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "sugarcrm_docs"

# LLM config (Ollama)
OLLAMA_BASE_URL = "http://localhost:11434/v1"
LLM_MODEL = "gpt-oss:20b"         # change to your preferred chat model
EMBEDDING_MODEL = "nomic-embed-text"

client_llm = OpenAI(
    base_url=OLLAMA_BASE_URL,
    api_key="ollama",
)

client_chroma = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client_chroma.get_or_create_collection(name=COLLECTION_NAME)


def embed_texts(texts: List[str]) -> List[List[float]]:
    resp = client_llm.embeddings.create(
        model=EMBEDDING_MODEL,
        input=texts,
    )
    return [d.embedding for d in resp.data]


def retrieve_context(query: str, k: int = 5) -> Tuple[str, List[dict]]:
    """Return a concatenated context string and raw metadata for top-k results."""
    query_emb = embed_texts([query])[0]
    results = collection.query(
        query_embeddings=[query_emb],
        n_results=k,
    )

    docs = results["documents"][0]
    metadatas = results["metadatas"][0]

    context_parts = []
    for doc, meta in zip(docs, metadatas):
        src = meta.get("source", "unknown")
        page = meta.get("page", "?")
        header = f"[Source: {src}, page {page}]"
        context_parts.append(f"{header}\n{doc}")

    context = "\n\n---\n\n".join(context_parts)
    return context, metadatas


def build_prompt(question: str, context: str) -> List[dict]:
    """Build a chat-style prompt for the LLM."""
    system_msg = (
        "You are SugarGPT, an expert assistant for SugarCRM. "
        "You answer questions using ONLY the provided context from the official "
        "SugarCRM documentation (dev, admin and application guides). "
        "If the answer is not in the context, say you don't know and suggest "
        "where in the docs the user might look."
    )

    user_msg = (
        "Here is the relevant documentation context:\n\n"
        f"{context}\n\n"
        "Now answer this question clearly and concisely. "
        "If helpful, reference the source file and page number.\n\n"
        f"Question: {question}"
    )

    return [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg},
    ]


def answer_question(question: str) -> str:
    """Full RAG pipeline: retrieve + generate answer."""
    if not question.strip():
        return "Please enter a question about SugarCRM."

    try:
        context, _ = retrieve_context(question, k=5)
        if not context:
            return "I couldn't find anything in the docs for that query."

        messages = build_prompt(question, context)

        resp = client_llm.chat.completions.create(
            model=LLM_MODEL,
            messages=messages,
            temperature=0.1,
        )

        return resp.choices[0].message.content.strip()

    except Exception as e:
        return f"Error: {e}"
