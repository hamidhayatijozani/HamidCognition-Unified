from __future__ import annotations

import os

from openai import OpenAI


SERVER_URL = os.environ["MCP_SERVER_URL"]
MODEL = os.getenv("OPENAI_MODEL", "gpt-5")


def main() -> None:
    client = OpenAI()
    response = client.responses.create(
        model=MODEL,
        input=os.getenv(
            "MCP_DEMO_PROMPT",
            "Use the HamidCognition MCP tool to read /public/info.txt and report the Action Gate decision and evidence.",
        ),
        tools=[
            {
                "type": "mcp",
                "server_label": "hamidcognition",
                "server_url": SERVER_URL,
                "allowed_tools": ["protected_read_public_file", "get_action_gate_evidence"],
                "require_approval": "never",
            }
        ],
    )
    print(response.output_text)


if __name__ == "__main__":
    main()
