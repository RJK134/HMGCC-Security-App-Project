"""Tests for PromptAdapter."""

from pathlib import Path
from unittest.mock import MagicMock

from core.database.connection import DatabaseManager
from core.models.profile import UserProfile
from core.profile.adapter import PromptAdapter
from core.profile.tracker import PreferenceTracker


def _make_adapter(tmp_path: Path) -> PromptAdapter:
    db = DatabaseManager(tmp_path / "adapt.db")
    db.initialize()
    return PromptAdapter(PreferenceTracker(db))


class TestPromptAdapter:
    def test_detailed_preference_adapts_prompt(self, tmp_path) -> None:
        adapter = _make_adapter(tmp_path)
        profile = UserProfile(detail_preference=0.8)
        result = adapter.adapt_system_prompt("Base prompt.", profile)
        assert "detailed" in result.lower()

    def test_concise_preference_adapts_prompt(self, tmp_path) -> None:
        adapter = _make_adapter(tmp_path)
        profile = UserProfile(detail_preference=0.2)
        result = adapter.adapt_system_prompt("Base prompt.", profile)
        assert "concise" in result.lower()

    def test_default_profile_no_change(self, tmp_path) -> None:
        adapter = _make_adapter(tmp_path)
        profile = UserProfile()  # defaults
        result = adapter.adapt_system_prompt("Base prompt.", profile)
        assert result == "Base prompt."

    def test_structured_format_adapts(self, tmp_path) -> None:
        adapter = _make_adapter(tmp_path)
        profile = UserProfile(format_preference="structured")
        result = adapter.adapt_system_prompt("Base prompt.", profile)
        assert "table" in result.lower() or "structured" in result.lower()

    def test_frequent_topics_in_prompt(self, tmp_path) -> None:
        adapter = _make_adapter(tmp_path)
        profile = UserProfile(frequent_topics=["spi", "firmware", "uart"])
        result = adapter.adapt_system_prompt("Base prompt.", profile)
        assert "spi" in result.lower()

    def test_suggest_related_queries_with_topics(self, tmp_path) -> None:
        adapter = _make_adapter(tmp_path)
        profile = UserProfile(frequent_topics=["spi", "firmware"])
        suggestions = adapter.suggest_related_queries(profile)
        assert len(suggestions) >= 2

    def test_suggest_related_queries_default(self, tmp_path) -> None:
        adapter = _make_adapter(tmp_path)
        profile = UserProfile()
        suggestions = adapter.suggest_related_queries(profile)
        assert len(suggestions) == 3  # Default suggestions

    def test_suggest_queries_max_three(self, tmp_path) -> None:
        adapter = _make_adapter(tmp_path)
        profile = UserProfile(frequent_topics=["a", "b", "c", "d", "e"])
        suggestions = adapter.suggest_related_queries(profile)
        assert len(suggestions) <= 3
