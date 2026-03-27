"""
local_file_io — OpenClaw skill: read and write text files inside the agent workspace only.

Why this exists (workshop + production):
- The LLM must never receive raw filesystem access; skills are the **enforcement layer**.
- Prompts say "be careful"; **code** guarantees paths stay under OPENCLAW_WORKSPACE_ROOT.

This module is safe to import in tests: behavior is driven by environment variables.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Literal

# ---------------------------------------------------------------------------
# Skill metadata — the runtime (or a registry) maps these to tool definitions
# ---------------------------------------------------------------------------
SKILL_NAME = "local_file_io"
SKILL_DESCRIPTION = (
    "Read or write UTF-8 text files only under the configured agent workspace. "
    "Refuses absolute paths and any path that resolves outside the workspace."
)


def _workspace_root() -> Path:
    """
    Root directory for all file operations.

    In Docker (see docker-compose.yml), OPENCLAW_WORKSPACE_ROOT is /workspace and
    maps to ./agent_workspace on the host. Tests override this via monkeypatch.
    """
    raw = os.environ.get("OPENCLAW_WORKSPACE_ROOT", "/workspace")
    return Path(raw).expanduser().resolve()


def _normalize_relative_path(relative_path: str) -> str:
    """
    Accept only non-absolute paths (POSIX or Windows-style roots rejected).

    We intentionally do **not** strip leading slashes from '/etc/passwd' — that would
    incorrectly turn it into a path inside the workspace.
    """
    p = relative_path.strip().replace("\\", "/")
    if not p or p == ".":
        raise ValueError("Path must be a non-empty relative path within the workspace.")
    if p.startswith("/") or p.startswith("\\"):
        raise PermissionError("Absolute paths are not allowed; use a path relative to the workspace.")
    # Windows: C:\... or \\server\share
    if len(p) >= 2 and p[1] == ":":
        raise PermissionError("Absolute paths are not allowed; use a path relative to the workspace.")
    if p.startswith("//"):
        raise PermissionError("Absolute paths are not allowed; use a path relative to the workspace.")
    return p


def _resolved_target(workspace: Path, relative_path: str) -> Path:
    """
    Join user path to workspace and resolve. Reject if the result leaves the workspace.

    Uses pathlib resolution so '..' and symlinks are handled consistently with the OS.
    """
    rel = _normalize_relative_path(relative_path)
    candidate = (workspace / rel).resolve()
    try:
        candidate.relative_to(workspace)
    except ValueError as exc:
        raise PermissionError(
            f"Path escapes workspace: {relative_path!r} is not allowed."
        ) from exc
    return candidate


def read_text(relative_path: str, max_bytes: int = 512_000) -> str:
    """
    Read a UTF-8 text file from the workspace.

    max_bytes caps accidental huge reads (tune per deployment).
    """
    workspace = _workspace_root()
    target = _resolved_target(workspace, relative_path)
    if not target.is_file():
        raise FileNotFoundError(f"Not a file: {relative_path}")
    data = target.read_bytes()
    if len(data) > max_bytes:
        raise ValueError(f"File exceeds max_bytes={max_bytes}.")
    return data.decode("utf-8")


def write_text(relative_path: str, content: str, create_parents: bool = True) -> dict[str, Any]:
    """
    Write UTF-8 text to a path inside the workspace. Optionally create parent dirs.

    Returns a small result dict suitable for logging / LLM consumption.
    """
    workspace = _workspace_root()
    target = _resolved_target(workspace, relative_path)
    if create_parents:
        target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    return {
        "ok": True,
        "path": relative_path,
        "bytes_written": len(content.encode("utf-8")),
    }


def run(
    action: Literal["read", "write"],
    path: str,
    content: str | None = None,
    *,
    create_parents: bool = True,
) -> dict[str, Any]:
    """
    Entry point expected by OpenClaw-style runtimes: one callable with an explicit action.

    This keeps the tool schema small and auditable.
    """
    action = action.lower().strip()  # type: ignore[assignment]
    if action == "read":
        text = read_text(path)
        return {"ok": True, "action": "read", "path": path, "content": text}
    if action == "write":
        if content is None:
            raise ValueError("write requires `content`.")
        meta = write_text(path, content, create_parents=create_parents)
        return {"ok": True, "action": "write", **meta}
    raise ValueError(f"Unknown action: {action!r}; expected 'read' or 'write'.")


# Optional: expose a dict for auto-registration in simple loaders
SKILL_EXPORT = {
    "name": SKILL_NAME,
    "description": SKILL_DESCRIPTION,
    "run": run,
}
