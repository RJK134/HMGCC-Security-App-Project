"""Repository for project CRUD operations."""

import sqlite3
from datetime import datetime, timezone
from uuid import UUID, uuid4

from core.models.project import Project


class ProjectRepository:
    """Data access layer for projects."""

    def create(self, conn: sqlite3.Connection, name: str, description: str | None = None) -> Project:
        """Create a new project.

        Args:
            conn: SQLite connection.
            name: Project name.
            description: Optional project description.

        Returns:
            The created Project.
        """
        now = datetime.now(timezone.utc).isoformat()
        project_id = str(uuid4())
        conn.execute(
            "INSERT INTO projects (id, name, description, created_at, updated_at) "
            "VALUES (?, ?, ?, ?, ?)",
            (project_id, name, description, now, now),
        )
        conn.commit()
        return Project(
            id=UUID(project_id),
            name=name,
            description=description,
            created_at=datetime.fromisoformat(now),
            updated_at=datetime.fromisoformat(now),
        )

    def get_by_id(self, conn: sqlite3.Connection, project_id: UUID) -> Project | None:
        """Get a project by ID.

        Args:
            conn: SQLite connection.
            project_id: Project UUID.

        Returns:
            Project if found, None otherwise.
        """
        row = conn.execute("SELECT * FROM projects WHERE id = ?", (str(project_id),)).fetchone()
        if row is None:
            return None

        doc_count = conn.execute(
            "SELECT COUNT(*) FROM documents WHERE project_id = ?", (str(project_id),)
        ).fetchone()[0]
        conv_count = conn.execute(
            "SELECT COUNT(*) FROM conversations WHERE project_id = ?", (str(project_id),)
        ).fetchone()[0]

        return Project(
            id=UUID(row["id"]),
            name=row["name"],
            description=row["description"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            document_count=doc_count,
            conversation_count=conv_count,
        )

    def list_all(self, conn: sqlite3.Connection) -> list[Project]:
        """List all projects.

        Args:
            conn: SQLite connection.

        Returns:
            List of all projects ordered by updated_at descending.
        """
        rows = conn.execute("SELECT * FROM projects ORDER BY updated_at DESC").fetchall()
        projects = []
        for row in rows:
            pid = row["id"]
            doc_count = conn.execute(
                "SELECT COUNT(*) FROM documents WHERE project_id = ?", (pid,)
            ).fetchone()[0]
            conv_count = conn.execute(
                "SELECT COUNT(*) FROM conversations WHERE project_id = ?", (pid,)
            ).fetchone()[0]
            projects.append(
                Project(
                    id=UUID(pid),
                    name=row["name"],
                    description=row["description"],
                    created_at=datetime.fromisoformat(row["created_at"]),
                    updated_at=datetime.fromisoformat(row["updated_at"]),
                    document_count=doc_count,
                    conversation_count=conv_count,
                )
            )
        return projects

    def update(
        self,
        conn: sqlite3.Connection,
        project_id: UUID,
        name: str | None = None,
        description: str | None = None,
    ) -> Project | None:
        """Update a project's name and/or description.

        Args:
            conn: SQLite connection.
            project_id: Project UUID to update.
            name: New name, or None to keep current.
            description: New description, or None to keep current.

        Returns:
            Updated Project, or None if not found.
        """
        existing = self.get_by_id(conn, project_id)
        if existing is None:
            return None

        new_name = name if name is not None else existing.name
        new_desc = description if description is not None else existing.description
        now = datetime.now(timezone.utc).isoformat()

        conn.execute(
            "UPDATE projects SET name = ?, description = ?, updated_at = ? WHERE id = ?",
            (new_name, new_desc, now, str(project_id)),
        )
        conn.commit()
        return self.get_by_id(conn, project_id)

    def delete(self, conn: sqlite3.Connection, project_id: UUID) -> bool:
        """Delete a project and all its associated data (cascading).

        Args:
            conn: SQLite connection.
            project_id: Project UUID to delete.

        Returns:
            True if deleted, False if not found.
        """
        cursor = conn.execute("DELETE FROM projects WHERE id = ?", (str(project_id),))
        conn.commit()
        return cursor.rowcount > 0
