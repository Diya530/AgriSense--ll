"""
RAG pipeline: markdown knowledge docs -> chunks -> embeddings -> ChromaDB -> retrieval.

Uses ChromaDB's built-in local embedding function (all-MiniLM-L6-v2 via onnxruntime)
so this works fully offline with no embedding API key or extra cost — practical for
a project this size, and easy to swap for a hosted embedding API later (see README).

The knowledge base is intentionally small and curated (data/knowledge/*.md) rather
than scraped at scale, so every fact traces back to a document we can point to.
Add more .md files to data/knowledge/ and call `rebuild_index()` to include them.
"""
import glob
import os
import re
from typing import List, Dict

from app.config import get_settings

_client = None
_collection = None


def _get_client_and_collection():
    global _client, _collection
    if _collection is not None:
        return _client, _collection

    settings = get_settings()
    try:
        import chromadb
    except ImportError as e:
        raise RuntimeError("chromadb not installed. Run: pip install chromadb") from e

    os.makedirs(settings.VECTOR_DB_DIR, exist_ok=True)
    _client = chromadb.PersistentClient(path=settings.VECTOR_DB_DIR)
    _collection = _client.get_or_create_collection(name="agri_knowledge")
    return _client, _collection


def _chunk_markdown(text: str, source: str, max_chars: int = 800) -> List[Dict]:
    """Chunk by markdown section (## headers), then further split long sections."""
    sections = re.split(r"\n(?=##? )", text)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        if len(section) <= max_chars:
            chunks.append({"text": section, "source": source})
        else:
            # split long sections into paragraph-sized pieces
            paras = [p.strip() for p in section.split("\n\n") if p.strip()]
            buf = ""
            for para in paras:
                if len(buf) + len(para) > max_chars and buf:
                    chunks.append({"text": buf, "source": source})
                    buf = para
                else:
                    buf = f"{buf}\n\n{para}" if buf else para
            if buf:
                chunks.append({"text": buf, "source": source})
    return chunks


def rebuild_index():
    """Wipes and rebuilds the vector index from all .md files in KNOWLEDGE_DIR."""
    settings = get_settings()
    client, _ = _get_client_and_collection()
    try:
        client.delete_collection("agri_knowledge")
    except Exception:
        pass
    global _collection
    _collection = client.get_or_create_collection(name="agri_knowledge")

    # Resolve relative to this file's location, not the process's working
    # directory, so this works the same locally and on any host regardless
    # of what directory the server was launched from.
    _here = os.path.dirname(os.path.abspath(__file__))       # backend/app/rag
    _backend_dir = os.path.dirname(os.path.dirname(_here))    # backend/
    knowledge_dir = os.path.normpath(os.path.join(_backend_dir, "..", "data", "knowledge"))
    files = glob.glob(os.path.join(knowledge_dir, "*.md"))

    all_chunks, all_ids, all_metas = [], [], []
    for filepath in files:
        source = os.path.basename(filepath)
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        chunks = _chunk_markdown(text, source)
        for i, chunk in enumerate(chunks):
            all_chunks.append(chunk["text"])
            all_ids.append(f"{source}::{i}")
            all_metas.append({"source": source})

    if all_chunks:
        _collection.add(documents=all_chunks, ids=all_ids, metadatas=all_metas)

    return {"files_indexed": len(files), "chunks_indexed": len(all_chunks)}


def retrieve(query: str, top_k: int = 4) -> List[Dict]:
    """Returns [{"text": str, "source": str, "distance": float}, ...]. Empty list
    (not an error) if the index is empty or nothing matches well — callers should
    fall back to general LLM reasoning and say the answer isn't from a specific doc."""
    try:
        _, collection = _get_client_and_collection()
        if collection.count() == 0:
            return []
        results = collection.query(query_texts=[query], n_results=top_k)
    except Exception:
        return []

    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    dists = results.get("distances", [[]])[0]

    return [
        {"text": doc, "source": meta.get("source", "unknown"), "distance": dist}
        for doc, meta, dist in zip(docs, metas, dists)
    ]
