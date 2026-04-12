"""Embedding generator using local Ollama models."""

from core.logging import get_logger
from core.models.document import Chunk
from core.rag.llm_client import OllamaClient

log = get_logger(__name__)


class Embedder:
    """Generate embeddings for document chunks using a local model.

    Args:
        ollama_client: Configured OllamaClient for embedding generation.
    """

    def __init__(self, ollama_client: OllamaClient) -> None:
        self._client = ollama_client

    def embed_chunks(self, chunks: list[Chunk], batch_size: int = 50) -> list[list[float]]:
        """Generate embedding vectors for a list of chunks.

        Processes in batches to manage memory. Retries once per batch on failure.

        Args:
            chunks: List of Chunk objects to embed.
            batch_size: Number of chunks per batch.

        Returns:
            List of embedding vectors, one per chunk.
        """
        texts = [c.content for c in chunks]
        all_embeddings: list[list[float]] = []
        total = len(texts)

        for i in range(0, total, batch_size):
            batch = texts[i : i + batch_size]
            batch_num = (i // batch_size) + 1
            total_batches = (total + batch_size - 1) // batch_size

            log.info(
                "embedding_batch",
                batch=batch_num,
                total_batches=total_batches,
                chunks=f"{i + 1}-{min(i + len(batch), total)}/{total}",
            )

            try:
                embeddings = self._client.generate_embeddings_batch(batch, batch_size=batch_size)
                all_embeddings.extend(embeddings)
            except Exception as e:
                log.warning("embedding_batch_failed_retrying", batch=batch_num, error=str(e))
                # Retry once
                try:
                    embeddings = self._client.generate_embeddings_batch(batch, batch_size=batch_size)
                    all_embeddings.extend(embeddings)
                except Exception as retry_err:
                    log.error(
                        "embedding_batch_failed",
                        batch=batch_num,
                        error=str(retry_err),
                    )
                    # Fill with empty vectors so indexing stays aligned
                    dim = len(all_embeddings[0]) if all_embeddings else 768
                    all_embeddings.extend([[0.0] * dim] * len(batch))

        return all_embeddings
