"""
RAG Vector Store — ChromaDB wrapper for storing and retrieving product documents.
"""
from __future__ import annotations
import os
from typing import List, Optional
from dotenv import load_dotenv

load_dotenv()

CHROMA_PATH = os.getenv("CHROMA_PATH", "./data/chroma_db")
COLLECTION_NAME = "product_documents"


def get_collection():
    """Get or create the ChromaDB collection."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=CHROMA_PATH)
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )
        return collection
    except Exception as e:
        print(f"[VectorStore] ChromaDB not available: {e}")
        return None


def add_document(
    doc_id: str,
    content: str,
    metadata: Optional[dict] = None,
) -> bool:
    """Add a document to the vector store."""
    collection = get_collection()
    if collection is None:
        return False
    try:
        collection.upsert(
            ids=[doc_id],
            documents=[content],
            metadatas=[metadata or {}],
        )
        return True
    except Exception as e:
        print(f"[VectorStore] Failed to add document: {e}")
        return False


def add_documents(
    doc_ids: List[str],
    contents: List[str],
    metadatas: Optional[List[dict]] = None,
) -> bool:
    """Add multiple documents to the vector store."""
    collection = get_collection()
    if collection is None:
        return False
    try:
        collection.upsert(
            ids=doc_ids,
            documents=contents,
            metadatas=metadatas or [{} for _ in doc_ids],
        )
        return True
    except Exception as e:
        print(f"[VectorStore] Failed to add documents: {e}")
        return False


def query_similar(
    query_text: str,
    n_results: int = 3,
    where: Optional[dict] = None,
) -> List[dict]:
    """
    Find documents similar to the query text.
    Returns a list of {id, content, metadata, distance} dicts.
    """
    collection = get_collection()
    if collection is None:
        return []
    try:
        kwargs = {
            "query_texts": [query_text],
            "n_results": min(n_results, max(1, collection.count())),
            "include": ["documents", "metadatas", "distances"],
        }
        if where:
            kwargs["where"] = where

        results = collection.query(**kwargs)

        output = []
        if results["documents"] and results["documents"][0]:
            for i, doc in enumerate(results["documents"][0]):
                output.append({
                    "id": results["ids"][0][i],
                    "content": doc,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0,
                })
        return output
    except Exception as e:
        print(f"[VectorStore] Query failed: {e}")
        return []


def get_document_count() -> int:
    """Return the number of documents in the collection."""
    collection = get_collection()
    if collection is None:
        return 0
    try:
        return collection.count()
    except Exception:
        return 0


def delete_document(doc_id: str) -> bool:
    """Remove a document from the collection."""
    collection = get_collection()
    if collection is None:
        return False
    try:
        collection.delete(ids=[doc_id])
        return True
    except Exception as e:
        print(f"[VectorStore] Delete failed: {e}")
        return False
