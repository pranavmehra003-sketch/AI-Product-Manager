"""
RAG Embeddings — Text chunking utilities for the vector store.
Uses ChromaDB's built-in embedding (no separate OpenAI embedding call needed
for basic usage, but can be upgraded to OpenAI embeddings).
"""
from __future__ import annotations
from typing import List


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 50) -> List[str]:
    """
    Split text into overlapping chunks for vector storage.
    
    Args:
        text: The text to chunk
        chunk_size: Characters per chunk
        overlap: Characters of overlap between chunks
    
    Returns:
        List of text chunks
    """
    if not text or len(text) <= chunk_size:
        return [text] if text else []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]

        # Try to break at a sentence boundary
        if end < len(text):
            last_period = chunk.rfind(". ")
            if last_period > chunk_size // 2:
                end = start + last_period + 1
                chunk = text[start:end]

        chunks.append(chunk.strip())
        start = end - overlap

    return [c for c in chunks if c.strip()]


def prepare_document(
    doc_id: str,
    title: str,
    content: str,
    doc_type: str = "general",
    chunk_size: int = 800,
) -> tuple[List[str], List[str], List[dict]]:
    """
    Prepare a document for vector store insertion.
    Chunks the content and generates IDs and metadata.
    
    Returns: (ids, contents, metadatas)
    """
    chunks = chunk_text(content, chunk_size=chunk_size)
    if not chunks:
        return [], [], []

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [
        {
            "doc_id": doc_id,
            "title": title,
            "doc_type": doc_type,
            "chunk_index": i,
            "total_chunks": len(chunks),
        }
        for i in range(len(chunks))
    ]

    return ids, chunks, metadatas


def clean_text(text: str) -> str:
    """Clean text before embedding: remove excess whitespace, normalize."""
    import re
    # Remove excessive newlines/spaces
    text = re.sub(r'\n{3,}', '\n\n', text)
    text = re.sub(r' {2,}', ' ', text)
    return text.strip()
