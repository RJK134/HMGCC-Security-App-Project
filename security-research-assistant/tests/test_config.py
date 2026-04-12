"""Tests for configuration management."""

import os

from backend.config import Settings


class TestSettings:
    """Tests for the Settings class."""

    def test_default_values(self) -> None:
        """Settings should have sensible defaults without any env vars."""
        settings = Settings()
        assert settings.ollama_base_url == "http://localhost:11434"
        assert settings.ollama_model == "mistral:7b-instruct-v0.3-q4_K_M"
        assert settings.ollama_embed_model == "nomic-embed-text"
        assert settings.chunk_size == 512
        assert settings.chunk_overlap == 50
        assert settings.top_k == 10
        assert settings.max_context_tokens == 4096
        assert settings.log_level == "INFO"

    def test_env_override(self, monkeypatch) -> None:
        """Environment variables with SRA_ prefix should override defaults."""
        monkeypatch.setenv("SRA_OLLAMA_MODEL", "llama3:8b")
        monkeypatch.setenv("SRA_CHUNK_SIZE", "1024")
        monkeypatch.setenv("SRA_LOG_LEVEL", "DEBUG")
        settings = Settings()
        assert settings.ollama_model == "llama3:8b"
        assert settings.chunk_size == 1024
        assert settings.log_level == "DEBUG"

    def test_chroma_dir_property(self) -> None:
        """chroma_dir property should return a resolved Path."""
        settings = Settings(chroma_path="./data/vectordb")
        assert settings.chroma_dir.is_absolute()

    def test_sqlite_file_property(self) -> None:
        """sqlite_file property should return a resolved Path."""
        settings = Settings(sqlite_path="./data/sqlite/sra.db")
        assert settings.sqlite_file.is_absolute()
        assert settings.sqlite_file.name == "sra.db"
