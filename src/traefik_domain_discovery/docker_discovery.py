from __future__ import annotations

import json
import subprocess
from typing import Any

from .models import DiscoveredHost
from .traefik_rules import parse_host_rules


ROUTER_RULE_PREFIX = "traefik.http.routers."
ROUTER_RULE_SUFFIX = ".rule"


def discover_from_docker() -> list[DiscoveredHost]:
    containers = _inspect_running_containers()
    discovered: list[DiscoveredHost] = []

    for container in containers:
        labels = container.get("Config", {}).get("Labels") or {}
        container_name = (container.get("Name") or "").lstrip("/") or container.get("Id", "")[:12]
        service_name = labels.get("com.docker.compose.service")
        compose_project = labels.get("com.docker.compose.project")

        for key, rule in labels.items():
            if not _is_router_rule_label(key):
                continue

            router_name = key.removeprefix(ROUTER_RULE_PREFIX).removesuffix(ROUTER_RULE_SUFFIX)
            for parsed in parse_host_rules(rule):
                discovered.append(
                    DiscoveredHost(
                        host=parsed.host,
                        source=container_name,
                        source_type="docker_label",
                        container_name=container_name,
                        service_name=service_name,
                        compose_project=compose_project,
                        router_name=router_name,
                        router_label_key=key,
                        rule=rule,
                        rule_type=parsed.rule_type,
                        regex_based=parsed.regex_based,
                        notes="HostRegexp requires review before use as a plain DNS target."
                        if parsed.regex_based
                        else None,
                    )
                )

    return discovered


def _inspect_running_containers() -> list[dict[str, Any]]:
    ids = _run_docker(["ps", "--quiet"]).splitlines()
    ids = [container_id for container_id in ids if container_id.strip()]
    if not ids:
        return []

    raw = _run_docker(["inspect", *ids])
    loaded = json.loads(raw)
    if not isinstance(loaded, list):
        raise RuntimeError("docker inspect returned an unexpected payload")
    return loaded


def _run_docker(args: list[str]) -> str:
    try:
        completed = subprocess.run(
            ["docker", *args],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("docker CLI was not found in PATH") from exc
    except subprocess.CalledProcessError as exc:
        message = exc.stderr.strip() or exc.stdout.strip() or str(exc)
        raise RuntimeError(f"docker {' '.join(args)} failed: {message}") from exc

    return completed.stdout


def _is_router_rule_label(key: str) -> bool:
    return key.startswith(ROUTER_RULE_PREFIX) and key.endswith(ROUTER_RULE_SUFFIX)

