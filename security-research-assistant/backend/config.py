"""Application configuration management using pydantic-settings.

Loads settings from environment variables (SRA_ prefix), falling back to
config.yaml, then to built-in defaults. Environment variables always win.
"""

from functools import lru_cache
from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


def _load_yaml_config() -> dict:
    """Load configuration from config.yaml if it exists.

    Returns:
        Dictionary of configuration values, or empty dict if file not found.
    """
    config_path = Path(__file__).resolve().parent.parent / "config.yaml"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
        # Flatten nested yaml structure to match settings field names
        flat: dict = {}
        for section in raw.values():
            if isinstance(section, dict):
                flat.update(section)
        return flat
    return {}


class _YamlDefaults(BaseSettings):
    """Internal settings class that loads yaml as defaults only.

    pydantic-settings resolves in order: init kwargs > env vars > .env > defaults.
    We inject yaml values as field defaults so env vars always win.
    """

    model_config = SettingsConfigDict(
        env_prefix="SRA_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# Build dynamic defaults from yaml
_yaml_cfg = _load_yaml_config()


class Settings(_YamlDefaults):
    """Application settings with SRA_ environment variable prefix.

    Priority: environment variables > .env file > config.yaml > built-in defaults.
    """

    # Ollama
    ollama_base_url: str = _yaml_cfg.get("base_url", "http://localhost:11434")
    ollama_model: str = _yaml_cfg.get("model", "mistral:7b-instruct-v0.3-q4_K_M")
    ollama_embed_model: str = _yaml_cfg.get("embed_model", "nomic-embed-text")

    # Storage paths
    chroma_path: str = _yaml_cfg.get("chroma_path", "./data/vectordb")
    sqlite_path: str = _yaml_cfg.get("sqlite_path", "./data/sqlite/sra.db")

    # Application
    log_level: str = _yaml_cfg.get("log_level", "INFO")
    host: str = _yaml_cfg.get("host", "127.0.0.1")
    port: int = _yaml_cfg.get("port", 8000)

    # RAG
    chunk_size: int = _yaml_cfg.get("chunk_size", 512)
    chunk_overlap: int = _yaml_cfg.get("chunk_overlap", 50)
    top_k: int = _yaml_cfg.get("top_k", 10)
    max_context_tokens: int = _yaml_cfg.get("max_context_tokens", 4096)

    @property
    def chroma_dir(self) -> Path:
        """Resolved ChromaDB storage directory."""
        return Path(self.chroma_path).resolve()

    @property
    def sqlite_file(self) -> Path:
        """Resolved SQLite database file path."""
        return Path(self.sqlite_path).resolve()


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached singleton Settings instance.

    Returns:
        Application settings loaded from env vars, config.yaml, and defaults.
    """
    return Settings()
