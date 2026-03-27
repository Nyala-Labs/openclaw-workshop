"""
Unit tests for skills/local_file_io.py — ensure the sandbox cannot be escaped.

Run from repo root: pytest tests/test_local_file_io.py -v
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Import skill from repo ./skills (workshop layout; not installed as a package)
_REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from skills import local_file_io as lf  # noqa: E402


@pytest.fixture
def workspace(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Each test gets an isolated workspace; skill reads OPENCLAW_WORKSPACE_ROOT."""
    root = tmp_path / "ws"
    root.mkdir()
    monkeypatch.setenv("OPENCLAW_WORKSPACE_ROOT", str(root))
    return root


def test_write_then_read_roundtrip(workspace: Path) -> None:
    lf.write_text("notes/hello.txt", "hello", create_parents=True)
    assert (workspace / "notes" / "hello.txt").read_text() == "hello"
    assert lf.read_text("notes/hello.txt") == "hello"


def test_absolute_path_rejected(workspace: Path) -> None:
    with pytest.raises((ValueError, PermissionError)):
        lf.read_text("/etc/passwd")


def test_parent_traversal_rejected(workspace: Path) -> None:
    (workspace / "safe.txt").write_text("inside")
    with pytest.raises(PermissionError):
        lf.read_text("../safe.txt")
    with pytest.raises(PermissionError):
        lf.read_text("a/../../outside")


def test_write_refuses_escape(workspace: Path) -> None:
    with pytest.raises(PermissionError):
        lf.write_text("../evil.txt", "x")


def test_run_read_write(workspace: Path) -> None:
    out = lf.run("write", "out/x.txt", content="ok")
    assert out["ok"] is True
    out2 = lf.run("read", "out/x.txt")
    assert out2["content"] == "ok"


def test_run_write_requires_content(workspace: Path) -> None:
    with pytest.raises(ValueError, match="content"):
        lf.run("write", "x.txt")
