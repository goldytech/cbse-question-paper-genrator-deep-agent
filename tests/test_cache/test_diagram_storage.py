"""Unit tests for diagram storage functionality."""

import json
import pytest
from pathlib import Path


class TestDiagramStorageInitialization:
    """Tests for diagram storage initialization."""

    def test_directory_creation(self, diagram_storage):
        """Verify diagrams directory is created."""
        assert Path(diagram_storage.base_dir).exists()

    def test_index_file_path(self, diagram_storage):
        """Verify index file path is set correctly."""
        assert diagram_storage.index_file == Path(diagram_storage.base_dir) / "diagram_index.json"


class TestDiagramStore:
    """Tests for storing diagrams."""

    def test_svg_file_created(self, diagram_storage):
        """Verify SVG file is created when storing."""
        key = "test_diagram_1"
        svg_content = "<svg><circle cx='50' cy='50' r='40'/></svg>"
        metadata = {"description": "Test circle", "type": "geometric"}

        diagram_storage.store(key, svg_content, metadata)

        svg_path = Path(diagram_storage.base_dir) / f"{key}.svg"
        assert svg_path.exists()

        with open(svg_path, "r") as f:
            assert f.read() == svg_content

    def test_index_updated(self, diagram_storage):
        """Verify index.json is updated when storing."""
        key = "test_diagram_2"
        svg_content = "<svg><rect width='100' height='100'/></svg>"
        metadata = {"description": "Test rectangle", "type": "geometric"}

        diagram_storage.store(key, svg_content, metadata)

        assert diagram_storage.index_file.exists()

        with open(diagram_storage.index_file, "r") as f:
            index = json.load(f)

        assert key in index
        assert index[key]["description"] == "Test rectangle"
        assert index[key]["type"] == "geometric"
        assert "filepath" in index[key]
        assert "created_at" in index[key]

    def test_store_multiple_diagrams(self, diagram_storage):
        """Verify multiple diagrams can be stored."""
        for i in range(3):
            key = f"diagram_{i}"
            svg = f"<svg><text>Diagram {i}</text></svg>"
            diagram_storage.store(key, svg, {"index": i})

        with open(diagram_storage.index_file, "r") as f:
            index = json.load(f)

        assert len(index) == 3


class TestDiagramRetrieve:
    """Tests for retrieving diagrams."""

    def test_retrieve_existing(self, diagram_storage):
        """Verify existing diagram can be retrieved."""
        key = "retrievable_diagram"
        svg_content = "<svg><polygon points='0,0 100,0 50,100'/></svg>"

        diagram_storage.store(key, svg_content, {})
        retrieved = diagram_storage.retrieve(key)

        assert retrieved == svg_content

    def test_retrieve_nonexistent_returns_none(self, diagram_storage):
        """Verify None returned for non-existent diagram."""
        retrieved = diagram_storage.retrieve("nonexistent_key")
        assert retrieved is None

    def test_retrieve_metadata(self, diagram_storage):
        """Verify metadata can be retrieved."""
        key = "metadata_test"
        metadata = {"chapter": "Triangles", "topic": "Pythagoras", "marks": 5}

        diagram_storage.store(key, "<svg></svg>", metadata)
        retrieved_metadata = diagram_storage.get_metadata(key)

        assert retrieved_metadata is not None
        assert retrieved_metadata["chapter"] == "Triangles"
        assert retrieved_metadata["marks"] == 5


class TestDiagramMetadata:
    """Tests for diagram metadata handling."""

    def test_complex_metadata(self, diagram_storage):
        """Verify complex metadata structures are stored."""
        key = "complex_meta"
        metadata = {
            "diagram_elements": {
                "shape": "right_triangle",
                "points": ["A", "B", "C"],
                "sides": ["AB=5", "BC=12", "AC=13"],
            },
            "tags": ["geometry", "pythagoras", "5-marks"],
        }

        diagram_storage.store(key, "<svg></svg>", metadata)
        retrieved = diagram_storage.get_metadata(key)

        assert retrieved["diagram_elements"]["shape"] == "right_triangle"
        assert len(retrieved["tags"]) == 3
