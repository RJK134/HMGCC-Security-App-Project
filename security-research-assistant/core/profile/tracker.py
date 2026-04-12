"""Implicit preference learning from user query patterns."""

import json
import re
from datetime import datetime, timezone
from uuid import UUID

from core.database.connection import DatabaseManager
from core.logging import get_logger
from core.models.profile import UserProfile
from core.models.query import QueryResponse

log = get_logger(__name__)

# Technical terms to track as topics
_TECH_PATTERNS = re.compile(
    r"\b(?:SPI|I2C|UART|CAN|GPIO|JTAG|USB|RS-\d+|Ethernet|Modbus|OPC-UA|MQTT|BACnet|"
    r"PROFINET|processor|memory|flash|SRAM|firmware|voltage|clock|frequency|register|"
    r"interrupt|DMA|ADC|DAC|PWM|timer|watchdog|bootloader|debug|schematic|datasheet|"
    r"PCB|protocol|interface|sensor|actuator|controller|transceiver|regulator)\b",
    re.IGNORECASE,
)

_DETAIL_KEYWORDS = {"explain", "detail", "elaborate", "more about", "tell me more", "describe", "in depth"}
_CONCISE_KEYWORDS = {"briefly", "summarise", "summary", "short", "quick", "just the"}
_TABLE_KEYWORDS = {"table", "list", "compare", "comparison", "versus", "vs"}
_PROSE_KEYWORDS = {"describe", "explain", "narrative", "overview"}

# Stabilisation: reduce learning rate after this many queries
_STABILISATION_THRESHOLD = 50


class PreferenceTracker:
    """Track and learn user preferences from query patterns.

    Args:
        db: Database manager for persisting profile data.
    """

    def __init__(self, db: DatabaseManager) -> None:
        self._db = db

    def track_query(
        self, user_query: str, response: QueryResponse, project_id: UUID
    ) -> None:
        """Update the user profile based on a completed query.

        Args:
            user_query: The user's question text.
            response: The generated response.
            project_id: Current project UUID.
        """
        profile = self.get_profile()
        now = datetime.now(timezone.utc)

        # Learning rate decreases after stabilisation
        lr = 1.0 if profile.query_count < _STABILISATION_THRESHOLD else 0.3

        # Topic frequencies
        topics = _TECH_PATTERNS.findall(user_query)
        for topic in topics:
            key = topic.lower()
            profile.topic_frequencies[key] = profile.topic_frequencies.get(key, 0) + 1

        # Detail preference
        query_lower = user_query.lower()
        if any(k in query_lower for k in _DETAIL_KEYWORDS):
            profile.detail_preference = min(1.0, profile.detail_preference + 0.05 * lr)
        elif any(k in query_lower for k in _CONCISE_KEYWORDS):
            profile.detail_preference = max(0.0, profile.detail_preference - 0.05 * lr)

        # Format preference
        if any(k in query_lower for k in _TABLE_KEYWORDS):
            profile.format_preference = "structured"
        elif any(k in query_lower for k in _PROSE_KEYWORDS):
            profile.format_preference = "prose"

        # Query count and timestamps
        profile.query_count += 1
        if profile.first_query_at is None:
            profile.first_query_at = now
        profile.last_query_at = now

        # Update frequent topics (top 10)
        sorted_topics = sorted(
            profile.topic_frequencies.items(), key=lambda x: x[1], reverse=True,
        )
        profile.frequent_topics = [t[0] for t in sorted_topics[:10]]

        self._save_profile(profile)

    def get_profile(self, user_id: str = "default") -> UserProfile:
        """Retrieve the current user profile.

        Args:
            user_id: User identifier (default for single-user MVP).

        Returns:
            UserProfile with current learned preferences.
        """
        conn = self._db.get_connection()
        self._ensure_table(conn)

        row = conn.execute(
            "SELECT preferences_json FROM user_profiles WHERE id = ?",
            (user_id,),
        ).fetchone()

        if row and row["preferences_json"]:
            try:
                data = json.loads(row["preferences_json"])
                return UserProfile(**data)
            except Exception:
                pass

        return UserProfile(user_id=user_id)

    def reset_profile(self, user_id: str = "default") -> None:
        """Clear all learned preferences and start fresh.

        Args:
            user_id: User identifier.
        """
        conn = self._db.get_connection()
        self._ensure_table(conn)
        now = datetime.now(timezone.utc).isoformat()
        conn.execute(
            "INSERT OR REPLACE INTO user_profiles (id, preferences_json, query_history_summary, created_at, updated_at) "
            "VALUES (?, '{}', '', ?, ?)",
            (user_id, now, now),
        )
        conn.commit()
        log.info("profile_reset", user_id=user_id)

    def export_profile(self, user_id: str = "default") -> dict:
        """Export profile as a JSON-serialisable dict.

        Args:
            user_id: User identifier.

        Returns:
            Profile data dict.
        """
        profile = self.get_profile(user_id)
        return profile.model_dump(mode="json")

    def import_profile(self, profile_data: dict, user_id: str = "default") -> None:
        """Import a previously exported profile.

        Args:
            profile_data: Profile dict to import.
            user_id: User identifier.
        """
        profile_data["user_id"] = user_id
        profile = UserProfile(**profile_data)
        self._save_profile(profile)
        log.info("profile_imported", user_id=user_id)

    def _save_profile(self, profile: UserProfile) -> None:
        """Persist profile to SQLite."""
        conn = self._db.get_connection()
        self._ensure_table(conn)
        now = datetime.now(timezone.utc).isoformat()
        data = profile.model_dump_json()
        conn.execute(
            "INSERT OR REPLACE INTO user_profiles (id, preferences_json, query_history_summary, created_at, updated_at) "
            "VALUES (?, ?, '', ?, ?)",
            (profile.user_id, data, now, now),
        )
        conn.commit()

    def _ensure_table(self, conn) -> None:  # type: ignore[no-untyped-def]
        """Ensure user_profiles table exists."""
        conn.execute("""
            CREATE TABLE IF NOT EXISTS user_profiles (
                id TEXT PRIMARY KEY,
                preferences_json TEXT DEFAULT '{}',
                query_history_summary TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
        """)
