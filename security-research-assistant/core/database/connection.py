"""SQLite connection manager with WAL mode for concurrent read performance."""

import sqlite3
from pathlib import Path

from core.database.schema import SCHEMA_SQL, SCHEMA_VERSION
from core.exceptions import DatabaseError
from core.logging import get_logger

log = get_logger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and initialization.

    Args:
        db_path: Path to the SQLite database file.
    """

    def __init__(self, db_path: Path) -> None:
        self._db_path = db_path
        self._connection: sqlite3.Connection | None = None

    def initialize(self) -> None:
        """Create the database file, tables, and indexes if they don't exist.

        Raises:
            DatabaseError: If database initialization fails.
        """
        try:
            self._db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = self.get_connection()
            conn.executescript(SCHEMA_SQL)

            # Record schema version
            conn.execute(
                "INSERT OR REPLACE INTO schema_version (id, version) VALUES (1, ?)",
                (SCHEMA_VERSION,),
            )
            conn.commit()
            log.info("database_initialized", path=str(self._db_path), version=SCHEMA_VERSION)
        except sqlite3.Error as e:
            raise DatabaseError(f"Failed to initialize database: {e}") from e

    def get_connection(self) -> sqlite3.Connection:
        """Return an open SQLite connection, creating one if needed.

        Returns:
            sqlite3.Connection configured with WAL mode and row factory.
        """
        if self._connection is None:
            self._connection = sqlite3.connect(
                str(self._db_path),
                check_same_thread=False,
            )
            self._connection.row_factory = sqlite3.Row
            self._connection.execute("PRAGMA journal_mode=WAL")
            self._connection.execute("PRAGMA foreign_keys=ON")
        return self._connection

    def close(self) -> None:
        """Close the database connection if open."""
        if self._connection is not None:
            self._connection.close()
            self._connection = None
            log.info("database_closed", path=str(self._db_path))
