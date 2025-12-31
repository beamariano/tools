"""Shared pytest fixtures and configuration."""

import pytest
from pathlib import Path
import tempfile
import shutil


@pytest.fixture
def temp_dir():
    """Create a temporary directory for testing."""
    temp_path = Path(tempfile.mkdtemp())
    yield temp_path
    shutil.rmtree(temp_path)


@pytest.fixture
def sample_image_path(temp_dir):
    """Create a sample image file path (doesn't create actual file)."""
    return temp_dir / "sample.jpg"


@pytest.fixture
def sample_video_path(temp_dir):
    """Create a sample video file path (doesn't create actual file)."""
    return temp_dir / "sample.mp4"


@pytest.fixture
def input_folder(temp_dir):
    """Create an input folder for testing."""
    folder = temp_dir / "input"
    folder.mkdir()
    return folder


@pytest.fixture
def output_folder(temp_dir):
    """Create an output folder for testing."""
    folder = temp_dir / "output"
    folder.mkdir()
    return folder
