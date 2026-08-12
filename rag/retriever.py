"""
RAG Retriever — High-level interface for retrieving relevant context.
Used by the PRD agent to find relevant past PRDs and product guidelines.
"""
from __future__ import annotations
import os
from pathlib import Path
from typing import List, Optional

from rag.vector_store import add_documents, query_similar, get_document_count
from rag.embeddings import prepare_document, clean_text


class ProductRetriever:
    """
    Manages the RAG pipeline for the AI Product Manager.
    
    Indexes: Previous PRDs, product guidelines, competitor reports.
    Retrieves: Relevant context for PRD generation.
    """

    def __init__(self):
        self._initialized = False

    def initialize(self, docs_dir: Optional[str] = None) -> None:
        """Load documents from the docs directory into the vector store."""
        if get_document_count() > 0:
            self._initialized = True
            return  # Already populated

        if docs_dir is None:
            docs_dir = os.path.join(os.path.dirname(__file__), "..", "docs")

        docs_path = Path(docs_dir)
        if not docs_path.exists():
            print("[Retriever] No docs directory found, skipping initialization.")
            self._initialized = True
            return

        loaded = 0
        for file_path in docs_path.rglob("*.md"):
            try:
                content = file_path.read_text(encoding="utf-8")
                doc_id = file_path.stem
                doc_type = file_path.parent.name

                ids, chunks, metadatas = prepare_document(
                    doc_id=doc_id,
                    title=file_path.stem.replace("_", " ").title(),
                    content=clean_text(content),
                    doc_type=doc_type,
                )
                if ids:
                    add_documents(ids, chunks, metadatas)
                    loaded += 1
            except Exception as e:
                print(f"[Retriever] Failed to load {file_path}: {e}")

        print(f"[Retriever] Indexed {loaded} documents. Total chunks: {get_document_count()}")
        self._initialized = True

    def add_prd(self, feature_name: str, prd_text: str) -> None:
        """Add a generated PRD to the vector store for future reference."""
        doc_id = f"prd_{feature_name.lower().replace(' ', '_')}"
        ids, chunks, metadatas = prepare_document(
            doc_id=doc_id,
            title=f"PRD: {feature_name}",
            content=clean_text(prd_text),
            doc_type="prd",
        )
        if ids:
            add_documents(ids, chunks, metadatas)

    def get_relevant_context(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant document chunks for a given query.
        Returns formatted text suitable for LLM consumption.
        """
        results = query_similar(query, n_results=n_results)
        if not results:
            return "No relevant context found in knowledge base."

        parts = []
        for r in results:
            title = r.get("metadata", {}).get("title", "Document")
            doc_type = r.get("metadata", {}).get("doc_type", "general")
            content = r.get("content", "")
            parts.append(f"### [{doc_type.upper()}] {title}\n{content}")

        return "\n\n---\n\n".join(parts)

    def get_similar_prds(self, feature_description: str) -> str:
        """Find past PRDs similar to the requested feature."""
        results = query_similar(
            feature_description,
            n_results=2,
        )
        if not results:
            return "No similar PRDs found."

        prd_results = [r for r in results if r.get("metadata", {}).get("doc_type") == "prd"]
        if not prd_results:
            return "No similar PRDs found."

        return self.get_relevant_context(feature_description, n_results=2)

    def get_document_stats(self) -> dict:
        """Return stats about the knowledge base."""
        count = get_document_count()
        return {"total_chunks": count, "initialized": self._initialized}


# Singleton retriever instance
_retriever: Optional[ProductRetriever] = None


def get_retriever() -> ProductRetriever:
    """Get the global retriever instance, initializing if needed."""
    global _retriever
    if _retriever is None:
        _retriever = ProductRetriever()
        _retriever.initialize()
    return _retriever
