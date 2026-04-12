"""Tests for PreferenceTracker."""

from pathlib import Path
from uuid import uuid4

import pytest

from core.database.connection import DatabaseManager
from core.models.query import ConfidenceResult, QueryResponse
from core.profile.tracker import PreferenceTracker


@pytest.fixture
def tracker(tmp_path: Path) -> PreferenceTracker:
    db = DatabaseManager(tmp_path / "profile.db")
    db.initialize()
    return PreferenceTracker(db)


def _make_response() -> QueryResponse:
    return QueryResponse(
        answer="Test answer", confidence=ConfidenceResult(score=80, explanation="Test"),
    )


class TestPreferenceTracker:
    def test_track_query_updates_topics(self, tracker) -> None:
        tracker.track_query("What SPI interface does the processor use?", _make_response(), uuid4())
        profile = tracker.get_profile()
        assert "spi" in profile.topic_frequencies
        assert "processor" in profile.topic_frequencies

    def test_detail_preference_increases(self, tracker) -> None:
        for _ in range(5):
            tracker.track_query("Explain the UART interface in detail", _make_response(), uuid4())
        profile = tracker.get_profile()
        assert profile.detail_preference > 0.5

    def test_detail_preference_decreases(self, tracker) -> None:
        for _ in range(5):
            tracker.track_query("Briefly summarise the GPIO pins", _make_response(), uuid4())
        profile = tracker.get_profile()
        assert profile.detail_preference < 0.5

    def test_query_count_increments(self, tracker) -> None:
        tracker.track_query("Test query about firmware", _make_response(), uuid4())
        tracker.track_query("Another query about memory", _make_response(), uuid4())
        profile = tracker.get_profile()
        assert profile.query_count == 2

    def test_frequent_topics_populated(self, tracker) -> None:
        for _ in range(3):
            tracker.track_query("Tell me about the SPI bus", _make_response(), uuid4())
        profile = tracker.get_profile()
        assert "spi" in profile.frequent_topics

    def test_reset_profile(self, tracker) -> None:
        tracker.track_query("SPI interface question", _make_response(), uuid4())
        tracker.reset_profile()
        profile = tracker.get_profile()
        assert profile.query_count == 0
        assert profile.topic_frequencies == {}

    def test_export_import_roundtrip(self, tracker) -> None:
        tracker.track_query("What firmware runs on the processor?", _make_response(), uuid4())
        exported = tracker.export_profile()
        tracker.reset_profile()
        tracker.import_profile(exported)
        profile = tracker.get_profile()
        assert profile.query_count == 1
        assert "firmware" in profile.topic_frequencies

    def test_format_preference_structured(self, tracker) -> None:
        tracker.track_query("Compare the interfaces in a table", _make_response(), uuid4())
        profile = tracker.get_profile()
        assert profile.format_preference == "structured"

    def test_default_profile_empty(self, tracker) -> None:
        profile = tracker.get_profile()
        assert profile.query_count == 0
        assert profile.detail_preference == 0.5
