"""Pytest configuration and shared fixtures."""

import pytest
import tempfile
import os


@pytest.fixture
def temp_md_file():
    """Create a temporary markdown file for testing."""
    def _create_file(content: str) -> str:
        fd, path = tempfile.mkstemp(suffix='.md')
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path
    
    paths = []
    
    def factory(content: str) -> str:
        path = _create_file(content)
        paths.append(path)
        return path
    
    yield factory
    
    # Cleanup
    for path in paths:
        if os.path.exists(path):
            os.unlink(path)


@pytest.fixture
def temp_jira_file():
    """Create a temporary Jira markup file for testing."""
    def _create_file(content: str) -> str:
        fd, path = tempfile.mkstemp(suffix='.jira')
        with os.fdopen(fd, 'w') as f:
            f.write(content)
        return path
    
    paths = []
    
    def factory(content: str) -> str:
        path = _create_file(content)
        paths.append(path)
        return path
    
    yield factory
    
    # Cleanup
    for path in paths:
        if os.path.exists(path):
            os.unlink(path)
