"""
MCP server entrypoint.

This entrypoint is cloud-friendly: it bootstraps PYTHONPATH/sys.path so that
imports like `modules.*` work even when the process cwd is not the repo root.
"""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path


# region agent log helper
DEBUG_LOG_PATH = "debug-978671.log"
DEBUG_SESSION_ID = "978671"


def _agent_log(*, run_id: str, hypothesis_id: str, location: str, message: str, data: dict) -> None:
    try:
        payload = {
            "sessionId": DEBUG_SESSION_ID,
            "runId": run_id,
            "hypothesisId": hypothesis_id,
            "location": location,
            "message": message,
            "data": data,
            "timestamp": int(time.time() * 1000),
        }
        with open(DEBUG_LOG_PATH, "a", encoding="utf-8") as f:
            f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    except Exception:
        pass


# endregion agent log helper


def _bootstrap_sys_path() -> None:
    repo_root = Path(__file__).resolve().parent
    repo_root_str = str(repo_root)

    if repo_root_str not in sys.path:
        sys.path.insert(0, repo_root_str)

    # 兼容部分云端平台通过 env 读取 PYTHONPATH
    current = os.environ.get("PYTHONPATH", "")
    if repo_root_str not in current.split(os.pathsep):
        os.environ["PYTHONPATH"] = (
            repo_root_str if not current else current + os.pathsep + repo_root_str
        )

    _agent_log(
        run_id="cloud",
        hypothesis_id="H-path",
        location="main.py:_bootstrap_sys_path",
        message="bootstrapped sys.path for repo root",
        data={
            "repo_root": repo_root_str,
            "cwd": os.getcwd(),
            "sys_path_head": sys.path[:5],
        },
    )


_bootstrap_sys_path()

# IMPORTANT: import after bootstrap
from MCP.itick_mcp import app  # noqa: E402


if __name__ == "__main__":
    app.run()
