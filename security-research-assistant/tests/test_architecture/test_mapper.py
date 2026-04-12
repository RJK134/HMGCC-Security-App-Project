"""Tests for architecture relationship mapper."""

from core.architecture.extractor import (
    ExtractedComponent,
    ExtractedInterface,
    ExtractedProtocol,
    ExtractedSoftware,
    ExtractionResult,
)
from core.architecture.mapper import ArchitectureMapper


class TestArchitectureMapper:
    def test_build_graph_from_extraction(self) -> None:
        extraction = ExtractionResult(
            components=[
                ExtractedComponent(name="STM32F407", component_type="processor"),
                ExtractedComponent(name="W25Q128", component_type="memory"),
            ],
            interfaces=[
                ExtractedInterface(name="SPI", connects_from="STM32F407", connects_to="W25Q128"),
            ],
            protocols=[ExtractedProtocol(name="Modbus RTU", layer="application")],
            software=[ExtractedSoftware(name="FreeRTOS", software_type="os", version="10.4")],
        )
        mapper = ArchitectureMapper()
        graph = mapper.build_graph(extraction)

        assert len(graph.nodes) >= 4  # 2 components + 1 protocol + 1 software
        assert len(graph.edges) >= 1
        node_ids = {n.id for n in graph.nodes}
        assert "stm32f407" in node_ids
        assert "w25q128" in node_ids

    def test_empty_extraction_shows_warnings(self) -> None:
        mapper = ArchitectureMapper()
        graph = mapper.build_graph(ExtractionResult())
        assert len(graph.incomplete_areas) > 0

    def test_edges_create_missing_nodes(self) -> None:
        extraction = ExtractionResult(
            interfaces=[
                ExtractedInterface(name="UART", connects_from="CPU", connects_to="Debug Port"),
            ],
        )
        mapper = ArchitectureMapper()
        graph = mapper.build_graph(extraction)
        node_ids = {n.id for n in graph.nodes}
        assert "cpu" in node_ids
        assert "debug_port" in node_ids
        assert len(graph.edges) == 1

    def test_node_groups_assigned(self) -> None:
        extraction = ExtractionResult(
            components=[ExtractedComponent(name="MCU", component_type="processor")],
            software=[ExtractedSoftware(name="Linux", software_type="os")],
            protocols=[ExtractedProtocol(name="MQTT")],
        )
        mapper = ArchitectureMapper()
        graph = mapper.build_graph(extraction)
        groups = {n.id: n.group for n in graph.nodes}
        assert groups["mcu"] == "hardware"
        assert groups["linux"] == "software"
        assert groups["mqtt"] == "protocol"
