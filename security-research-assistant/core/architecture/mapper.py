"""Relationship mapping — build a graph of component connections."""

from pydantic import BaseModel, Field

from core.architecture.extractor import ExtractionResult
from core.logging import get_logger

log = get_logger(__name__)


class GraphNode(BaseModel):
    """A node in the architecture graph."""
    id: str
    label: str
    node_type: str  # processor, memory, sensor, protocol, software, etc.
    description: str = ""
    group: str = ""  # For visual grouping (hardware, software, protocol)


class GraphEdge(BaseModel):
    """An edge (connection) in the architecture graph."""
    source: str  # node id
    target: str  # node id
    label: str = ""  # interface name
    edge_type: str = "connection"  # connection, protocol, depends_on


class ArchitectureGraph(BaseModel):
    """Complete architecture graph for visualisation."""
    nodes: list[GraphNode] = Field(default_factory=list)
    edges: list[GraphEdge] = Field(default_factory=list)
    summary: str = ""
    incomplete_areas: list[str] = Field(default_factory=list)


class ArchitectureMapper:
    """Build a graph representation from extracted components and interfaces."""

    def build_graph(self, extraction: ExtractionResult) -> ArchitectureGraph:
        """Convert extraction results into a graph of nodes and edges.

        Args:
            extraction: Result from ArchitectureExtractor.

        Returns:
            ArchitectureGraph ready for visualisation and export.
        """
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        node_ids: set[str] = set()

        def _make_id(name: str) -> str:
            return name.lower().replace(" ", "_").replace("-", "_")[:40]

        # Components → nodes
        for comp in extraction.components:
            nid = _make_id(comp.name)
            if nid not in node_ids:
                nodes.append(GraphNode(
                    id=nid, label=comp.name,
                    node_type=comp.component_type,
                    description=comp.description,
                    group="hardware",
                ))
                node_ids.add(nid)

        # Software → nodes
        for sw in extraction.software:
            nid = _make_id(sw.name)
            if nid not in node_ids:
                nodes.append(GraphNode(
                    id=nid, label=sw.name,
                    node_type=sw.software_type or "software",
                    description=f"v{sw.version}" if sw.version else "",
                    group="software",
                ))
                node_ids.add(nid)

        # Protocols → nodes
        for proto in extraction.protocols:
            nid = _make_id(proto.name)
            if nid not in node_ids:
                nodes.append(GraphNode(
                    id=nid, label=proto.name,
                    node_type="protocol",
                    description=proto.description,
                    group="protocol",
                ))
                node_ids.add(nid)

        # Interfaces → edges (and ensure endpoint nodes exist)
        for iface in extraction.interfaces:
            src_id = _make_id(iface.connects_from) if iface.connects_from else ""
            tgt_id = _make_id(iface.connects_to) if iface.connects_to else ""

            # Create missing nodes
            if src_id and src_id not in node_ids:
                nodes.append(GraphNode(id=src_id, label=iface.connects_from, node_type="other", group="hardware"))
                node_ids.add(src_id)
            if tgt_id and tgt_id not in node_ids:
                nodes.append(GraphNode(id=tgt_id, label=iface.connects_to, node_type="other", group="hardware"))
                node_ids.add(tgt_id)

            if src_id and tgt_id:
                edges.append(GraphEdge(
                    source=src_id, target=tgt_id,
                    label=iface.name, edge_type="connection",
                ))

        # Identify incomplete areas
        incomplete: list[str] = []
        if not extraction.components:
            incomplete.append("No hardware components identified — more datasheets may be needed.")
        if not extraction.interfaces:
            incomplete.append("No interfaces mapped — schematics or wiring diagrams would help.")
        if not extraction.protocols:
            incomplete.append("No communication protocols identified.")
        if not extraction.software:
            incomplete.append("No software components found — firmware or code files may be needed.")

        graph = ArchitectureGraph(
            nodes=nodes, edges=edges, incomplete_areas=incomplete,
        )

        log.info(
            "architecture_graph_built",
            nodes=len(nodes), edges=len(edges),
            incomplete=len(incomplete),
        )
        return graph
