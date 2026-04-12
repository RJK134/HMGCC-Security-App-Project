"""Non-English content detection and translation using local LLM."""

from pydantic import BaseModel

from core.logging import get_logger
from core.rag.llm_client import OllamaClient

log = get_logger(__name__)


class TranslatedText(BaseModel):
    """Result of a text translation."""
    original_text: str
    translated_text: str
    source_language: str
    confidence: float = 0.0


class Translator:
    """Detect and translate non-English content using the local LLM.

    Args:
        ollama_client: Local LLM for translation.
    """

    def __init__(self, ollama_client: OllamaClient) -> None:
        self._llm = ollama_client

    def detect_language(self, text: str) -> str:
        """Detect the language of a text sample.

        Args:
            text: Text to analyse (first 500 chars used).

        Returns:
            Language name string (e.g., "English", "German").
        """
        sample = text[:500]
        prompt = (
            "What language is this text written in? Respond with just the language name, "
            f"nothing else.\n\nText: {sample}"
        )
        try:
            response = self._llm.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)
            return response.strip().split("\n")[0].strip()
        except Exception as e:
            log.warning("language_detection_failed", error=str(e))
            return "Unknown"

    def translate_to_english(self, text: str, source_language: str) -> TranslatedText:
        """Translate text to English, preserving technical terms.

        Args:
            text: Text to translate.
            source_language: Source language name.

        Returns:
            TranslatedText with original and translated content.
        """
        prompt = (
            f"Translate the following {source_language} text to English.\n"
            "Preserve all technical terms, part numbers, and measurements exactly as written.\n"
            "Only translate the natural language portions.\n\n"
            f"Text: {text}"
        )
        try:
            response = self._llm.generate(prompt, system_prompt="")
            if not isinstance(response, str):
                response = "".join(response)
            return TranslatedText(
                original_text=text,
                translated_text=response.strip(),
                source_language=source_language,
                confidence=0.7,
            )
        except Exception as e:
            log.warning("translation_failed", error=str(e))
            return TranslatedText(
                original_text=text,
                translated_text=text,  # Fallback to original
                source_language=source_language,
                confidence=0.0,
            )

    def is_english(self, text: str) -> bool:
        """Quick heuristic check if text is primarily English.

        Args:
            text: Text sample to check.

        Returns:
            True if text appears to be English.
        """
        # Simple heuristic: check for common English words
        common = {"the", "is", "and", "of", "to", "in", "for", "that", "with", "on"}
        words = set(text.lower().split()[:100])
        english_count = len(words & common)
        return english_count >= 3
