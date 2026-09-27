from __future__ import annotations

from typing import Any, Protocol


class ToolPlugin(Protocol):
    plugin_id: str

    def verify_authority(self, token: str, policy_id: str, action_id: str, nonce: str) -> None: ...
    def report_execution(self, evidence_id: str, result_digest: str) -> None: ...
    def enforce_fail_closed(self, reason: str) -> None: ...


class MCPPlugin(ToolPlugin, Protocol):
    server_id: str

    def call(self, tool: str, arguments: dict[str, Any]) -> Any: ...
