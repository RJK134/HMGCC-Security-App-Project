"""Tests for Pydantic data models."""

from uuid import uuid4

from core.models.conversation import Citation, Conversation, Message, MessageRole, PinnedFact
from core.models.document import Chunk, DocumentMetadata, DocumentStatus, DocumentType, SourceTier
from core.models.project import Project
from core.models.query import ConfidenceResult, QueryRequest, QueryResponse


class TestDocumentModels:
    """Tests for document-related models."""

    def test_document_metadata_defaults(self) -> None:
        """DocumentMetadata should generate id, timestamp, and defaults."""
        doc = DocumentMetadata(
            project_id=uuid4(),
            filename="datasheet.pdf",
            filepath="/tmp/datasheet.pdf",
            filetype=DocumentType.PDF,
            size_bytes=1024,
        )
        assert doc.id is not None
        assert doc.status == DocumentStatus.PENDING
        assert doc.source_tier == SourceTier.TIER_4_UNVERIFIED
        assert doc.import_timestamp is not None
        assert doc.metadata == {}

    def test_chunk_creation(self) -> None:
        """Chunk should store content and metadata."""
        chunk = Chunk(
            document_id=uuid4(),
            content="STM32F407 datasheet excerpt",
            chunk_index=0,
            page_number=3,
            section_heading="Pin Configuration",
            token_count=42,
            chroma_id="chunk_001",
        )
        assert chunk.content == "STM32F407 datasheet excerpt"
        assert chunk.page_number == 3

    def test_document_type_enum(self) -> None:
        """DocumentType enum values should be lowercase strings."""
        assert DocumentType.PDF.value == "pdf"
        assert DocumentType.IMAGE.value == "image"
        assert DocumentType.CODE.value == "code"

    def test_source_tier_enum(self) -> None:
        """SourceTier enum values should follow naming convention."""
        assert SourceTier.TIER_1_MANUFACTURER.value == "tier_1_manufacturer"
        assert SourceTier.TIER_4_UNVERIFIED.value == "tier_4_unverified"


class TestConversationModels:
    """Tests for conversation-related models."""

    def test_message_creation(self) -> None:
        """Message should store role, content, and optional citations."""
        msg = Message(
            conversation_id=uuid4(),
            role=MessageRole.USER,
            content="What processor does this board use?",
        )
        assert msg.role == MessageRole.USER
        assert msg.citations == []
        assert msg.confidence_score is None

    def test_citation_creation(self) -> None:
        """Citation should reference a document chunk."""
        citation = Citation(
            document_id=uuid4(),
            document_name="STM32F407_datasheet.pdf",
            page_number=5,
            chunk_id="chunk_042",
            relevance_score=0.92,
            excerpt="The STM32F407 features an ARM Cortex-M4 core",
        )
        assert citation.relevance_score == 0.92
        assert citation.page_number == 5

    def test_conversation_defaults(self) -> None:
        """Conversation should initialize with empty messages and pinned facts."""
        conv = Conversation(
            project_id=uuid4(),
            title="Board Analysis",
        )
        assert conv.messages == []
        assert conv.pinned_facts == []
        assert conv.summary is None

    def test_pinned_fact(self) -> None:
        """PinnedFact should store content and optional source refs."""
        fact = PinnedFact(
            conversation_id=uuid4(),
            content="Main processor is STM32F407VGT6",
        )
        assert fact.source_refs == []


class TestQueryModels:
    """Tests for query-related models."""

    def test_query_request(self) -> None:
        """QueryRequest should require question and project_id."""
        req = QueryRequest(
            question="What interfaces does the main processor expose?",
            project_id=uuid4(),
        )
        assert req.conversation_id is None

    def test_confidence_result_bounds(self) -> None:
        """ConfidenceResult score must be between 0 and 100."""
        result = ConfidenceResult(
            score=85.5,
            explanation="High confidence: 3 corroborating Tier 1 sources.",
        )
        assert 0 <= result.score <= 100

    def test_query_response(self) -> None:
        """QueryResponse should contain answer, citations, and confidence."""
        response = QueryResponse(
            answer="The main processor is an ARM Cortex-M4.",
            confidence=ConfidenceResult(score=90, explanation="Well-sourced"),
            sources_used=3,
        )
        assert response.sources_used == 3
        assert response.citations == []


class TestProjectModel:
    """Tests for the Project model."""

    def test_project_defaults(self) -> None:
        """Project should initialize with zero counts and timestamps."""
        project = Project(name="ICS Investigation")
        assert project.document_count == 0
        assert project.conversation_count == 0
        assert project.description is None
        assert project.id is not None
