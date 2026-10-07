#!/usr/bin/env python3
"""Generate a factual runtime evidence capsule.

This module reports observations from the local host and Docker runtime.
It deliberately does not label self-reported host properties as trusted facts.
"""

from __future__ import annotations

import hashlib
import json
import os
import platform
import socket
import subprocess
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "evidence" / "runtime" / "runtime-capsule.json"
COMPOSE = ROOT / "action_gate" / "docker-compose.production.yml"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def run(*args: str) -> str | None:
    try:
        p = subprocess.run(
            args, cwd=ROOT, text=True, capture_output=True, timeout=15, check=False
        )
        if p.returncode == 0:
            return p.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        pass
    return None


def git_sha() -> str | None:
    return run("git", "rev-parse", "HEAD")


def docker_containers() -> list[dict]:
    raw = run(
        "docker", "ps", "-a", "--format",
        "{{json .}}"
    )
    if not raw:
        return []
    rows = []
    for line in raw.splitlines():
        try:
            item = json.loads(line)
            rows.append({
                "name": item.get("Names"),
                "image": item.get("Image"),
                "state": item.get("State"),
                "status": item.get("Status"),
            })
        except json.JSONDecodeError:
            continue
    return rows


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)

    capsule = {
        "capsule_version": "1",
        "runtime_id": os.environ.get("RUNTIME_ID", f"{socket.gethostname()}-{int(time.time())}"),
        "runtime_version": os.environ.get("RUNTIME_VERSION", "portable-0.1.0"),
        "observed_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "git_sha": git_sha(),
        "host": {
            "hostname": socket.gethostname(),
            "platform": platform.platform(),
            "python_version": platform.python_version(),
            "state": "OBSERVED",
        },
        "compose": {
            "path": str(COMPOSE.relative_to(ROOT)),
            "sha256": sha256_file(COMPOSE) if COMPOSE.exists() else None,
            "state": "OBSERVED",
        },
        "docker": {
            "version": run("docker", "--version"),
            "compose_version": run("docker", "compose", "version"),
            "containers": docker_containers(),
            "state": "OBSERVED",
        },
        "policy_hash": os.environ.get("ACTION_GATE_POLICY_HASH"),
        "database_schema": os.environ.get("ACTION_GATE_SCHEMA_VERSION"),
        "health": "OBSERVED",
        "truth_boundary": {
            "self_reported_host_properties_are_not_trusted": True,
            "capsule_is_an_observation_record": True,
            "cryptographic_attestation_required_for_verified_host_identity": True,
        },
    }

    OUT.write_text(
        json.dumps(capsule, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(OUT)


if __name__ == "__main__":
    main()
