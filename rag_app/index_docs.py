# index_docs.py
import os
import uuid
from typing import List, Dict

from pypdf import PdfReader
import chromadb
from openai import OpenAI

# === CONFIG ===
PDF_DIR = "docs"
CHROMA_DIR = "chroma_db"
COLLECTION_NAME = "sugarcrm_docs"

# Ollama as OpenAI-compatible server
client = OpenAI(
    base_url="http://localhost:11434/v1",
    api_key="ollama",  # required, but unused
)

EMBEDDING_MODEL = "nomic-embed-text"  # same one you used in test_embed.py


def embed_text(text: str) -> List[float]:
    """Get embedding for a single string using Ollama."""
    resp = client.embeddings.create(
        model=EMBEDDING_MODEL,
        input=[text],  # list of 1, like in test_embed.py
    )
    return resp.data[0].embedding


def load_pdfs(pdf_dir: str) -> List[Dict]:
    """Read all PDFs and return list of {text, metadata} chunks."""
    chunks = []

    for filename in os.listdir(pdf_dir):
        if not filename.lower().endswith(".pdf"):
            continue

        path = os.path.join(pdf_dir, filename)
        print(f"Reading {path}...")
        reader = PdfReader(path)

        for page_num, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            text = text.strip()
            if not text:
                continue

            # simple character-based chunking
            chunk_size = 1500
            overlap = 200

            start = 0
            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end]

                chunks.append(
                    {
                        "text": chunk_text,
                        "metadata": {
                            "source": filename,
                            "page": page_num + 1,
                        },
                    }
                )

                start = end - overlap  # overlap with previous chunk

    return chunks


def main():
    # 0) Start fresh
    if os.path.exists(CHROMA_DIR):
        print(f"Removing existing Chroma DB at {CHROMA_DIR}...")
        import shutil
        shutil.rmtree(CHROMA_DIR)

    # 1) Load & chunk PDFs
    print("Loading and chunking PDFs...")
    chunks = load_pdfs(PDF_DIR)
    print(f"Total chunks: {len(chunks)}")

    # 2) Init Chroma
    client_chroma = chromadb.PersistentClient(path=CHROMA_DIR)
    collection = client_chroma.get_or_create_collection(name=COLLECTION_NAME)

    # 3) Add to Chroma, one chunk at a time
    total = len(chunks)
    for i, chunk in enumerate(chunks, start=1):
        text = chunk["text"]
        metadata = chunk["metadata"]
        doc_id = str(uuid.uuid4())

        # progress indicator
        if i % 50 == 0 or i == 1:
            print(f"Embedding chunk {i}/{total} (source={metadata['source']}, page={metadata['page']})...")

        try:
            embedding = embed_text(text)
        except Exception as e:
            print(f"!! Error embedding chunk {i}: {e}")
            continue  # skip this chunk but keep going

        collection.add(
            ids=[doc_id],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata],
        )

    print("Done. Chroma index built in:", CHROMA_DIR)
    print("Total vectors in collection:", collection.count())


if __name__ == "__main__":
    main()
