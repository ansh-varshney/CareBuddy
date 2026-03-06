"""RAG Pipeline — Retrieval-Augmented Generation using ChromaDB."""

import logging
from typing import Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class RAGRetriever:
    """
    Retrieves relevant medical knowledge from ChromaDB vector store
    to augment LLM responses with grounded information.
    """

    def __init__(self):
        self._client: Optional[chromadb.ClientAPI] = None
        self._collection = None

    def _get_client(self) -> chromadb.ClientAPI:
        """Lazy-initialize ChromaDB client."""
        if self._client is None:
            self._client = chromadb.PersistentClient(
                path=settings.CHROMA_PERSIST_DIR,
                settings=ChromaSettings(anonymized_telemetry=False),
            )
        return self._client

    def warm_up(self) -> None:
        """Pre-initialize ChromaDB at startup to avoid cold-start on first request."""
        try:
            collection = self._get_collection()
            count = collection.count()
            logger.info(f"🔥 ChromaDB warmed up: {count} documents in '{settings.CHROMA_COLLECTION_NAME}'")
        except Exception as e:
            logger.warning(f"ChromaDB warm-up failed (non-fatal): {e}")

    def _get_collection(self):
        """Get or create the medical knowledge collection."""
        if self._collection is None:
            client = self._get_client()
            self._collection = client.get_or_create_collection(
                name=settings.CHROMA_COLLECTION_NAME,
                metadata={"description": "Medical knowledge base for CareBuddy"},
            )
        return self._collection

    async def retrieve(self, query: str, n_results: int = 3) -> str:
        """
        Retrieve relevant medical documents for a query.

        Args:
            query: User's health question or symptom description
            n_results: Number of relevant documents to retrieve

        Returns:
            Concatenated relevant context string, or empty string if none found
        """
        try:
            collection = self._get_collection()

            # Check if collection has any documents
            if collection.count() == 0:
                logger.info("Knowledge base is empty — skipping RAG retrieval")
                return ""

            results = collection.query(
                query_texts=[query],
                n_results=min(n_results, collection.count()),
            )

            if not results["documents"] or not results["documents"][0]:
                return ""

            # Combine retrieved documents with source metadata
            context_parts = []
            for i, doc in enumerate(results["documents"][0]):
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                source = metadata.get("source", "Medical Reference")
                context_parts.append(f"[Source: {source}]\n{doc}")

            return "\n\n".join(context_parts)

        except Exception as e:
            logger.error(f"RAG retrieval error: {e}")
            return ""

    def add_documents(
        self,
        documents: list[str],
        metadatas: list[dict],
        ids: list[str],
    ) -> None:
        """
        Add documents to the knowledge base.

        Args:
            documents: List of text chunks
            metadatas: List of metadata dicts (source, category, etc.)
            ids: List of unique document IDs
        """
        collection = self._get_collection()
        # ChromaDB handles embedding automatically with its default model
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
        )
        logger.info(f"Added {len(documents)} documents to knowledge base")

    def get_stats(self) -> dict:
        """Get knowledge base statistics."""
        collection = self._get_collection()
        return {
            "total_documents": collection.count(),
            "collection_name": settings.CHROMA_COLLECTION_NAME,
        }


# Global RAG retriever instance
rag_retriever = RAGRetriever()
