"""Ollama LLM client for local inference and embedding generation.

Connects to localhost only — no external network calls.
"""

from collections.abc import Generator

import ollama as ollama_lib

from core.exceptions import LLMConnectionError, LLMInferenceError
from core.logging import get_logger

log = get_logger(__name__)


class OllamaClient:
    """Client for the local Ollama LLM server.

    Args:
        base_url: Ollama server URL (must be localhost).
        model_name: Name of the chat/generation model.
        embed_model_name: Name of the embedding model.
    """

    def __init__(
        self,
        base_url: str = "http://localhost:11434",
        model_name: str = "mistral:7b-instruct-v0.3-q4_K_M",
        embed_model_name: str = "nomic-embed-text",
    ) -> None:
        self._base_url = base_url
        self._model_name = model_name
        self._embed_model_name = embed_model_name
        self._client = ollama_lib.Client(host=base_url)

    def health_check(self) -> bool:
        """Check if Ollama is reachable and the configured model is available.

        Returns:
            True if Ollama responds and the model is listed.
        """
        try:
            models = self.list_models()
            log.debug("ollama_health_check", available_models=models)
            return True
        except LLMConnectionError:
            return False

    def list_models(self) -> list[str]:
        """List all models available on the local Ollama instance.

        Returns:
            List of model name strings.

        Raises:
            LLMConnectionError: If Ollama is unreachable.
        """
        try:
            response = self._client.list()
            return [m.model for m in response.models]
        except Exception as e:
            raise LLMConnectionError(
                f"Cannot connect to Ollama at {self._base_url}: {e}"
            ) from e

    def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        stream: bool = False,
    ) -> str | Generator[str, None, None]:
        """Generate a response from the local LLM.

        Args:
            prompt: User prompt text.
            system_prompt: System instructions for the model.
            stream: If True, returns a generator yielding response chunks.

        Returns:
            Complete response string, or a generator of chunks if stream=True.

        Raises:
            LLMInferenceError: If generation fails.
        """
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            if stream:
                return self._stream_generate(messages)
            response = self._client.chat(model=self._model_name, messages=messages)
            return response.message.content
        except Exception as e:
            raise LLMInferenceError(
                f"LLM generation failed: {e}", details={"model": self._model_name}
            ) from e

    def _stream_generate(self, messages: list[dict]) -> Generator[str, None, None]:
        """Stream response tokens from the LLM.

        Args:
            messages: Chat messages list.

        Yields:
            Response text chunks as they arrive.
        """
        try:
            stream = self._client.chat(
                model=self._model_name, messages=messages, stream=True
            )
            for chunk in stream:
                if chunk.message.content:
                    yield chunk.message.content
        except Exception as e:
            raise LLMInferenceError(
                f"LLM streaming failed: {e}", details={"model": self._model_name}
            ) from e

    def generate_embedding(self, text: str) -> list[float]:
        """Generate an embedding vector for a single text.

        Args:
            text: Input text to embed.

        Returns:
            Embedding vector as a list of floats.

        Raises:
            LLMConnectionError: If embedding generation fails.
        """
        try:
            response = self._client.embed(model=self._embed_model_name, input=text)
            return response.embeddings[0]
        except Exception as e:
            raise LLMConnectionError(
                f"Embedding generation failed: {e}",
                details={"model": self._embed_model_name},
            ) from e

    def generate_embeddings_batch(
        self, texts: list[str], batch_size: int = 32
    ) -> list[list[float]]:
        """Generate embeddings for multiple texts in batches.

        Args:
            texts: List of input texts.
            batch_size: Number of texts per batch.

        Returns:
            List of embedding vectors, one per input text.

        Raises:
            LLMConnectionError: If embedding generation fails.
        """
        all_embeddings: list[list[float]] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            try:
                response = self._client.embed(model=self._embed_model_name, input=batch)
                all_embeddings.extend(response.embeddings)
                log.debug(
                    "embeddings_batch_complete",
                    batch_start=i,
                    batch_size=len(batch),
                    total=len(texts),
                )
            except Exception as e:
                raise LLMConnectionError(
                    f"Batch embedding failed at index {i}: {e}",
                    details={"model": self._embed_model_name, "batch_start": i},
                ) from e
        return all_embeddings
