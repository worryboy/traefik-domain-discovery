from __future__ import annotations

from pathlib import Path
from typing import Any

from .models import DiscoveredHost
from .traefik_rules import parse_host_rules
from . import yaml_compat as yaml


def discover_from_file_provider(config_dir: str | Path) -> list[DiscoveredHost]:
    root = Path(config_dir).expanduser()
    if not root.exists():
        raise FileNotFoundError(f"file provider directory does not exist: {root}")
    if not root.is_dir():
        raise NotADirectoryError(f"file provider path is not a directory: {root}")

    discovered: list[DiscoveredHost] = []
    for path in sorted(_iter_yaml_files(root)):
        with path.open("r", encoding="utf-8") as handle:
            payload = yaml.safe_load(handle.read()) or {}
        if not isinstance(payload, dict):
            continue
        discovered.extend(_discover_from_payload(payload, path))

    return discovered


def _iter_yaml_files(root: Path) -> list[Path]:
    patterns = ("*.yaml", "*.yml")
    files: list[Path] = []
    for pattern in patterns:
        files.extend(root.rglob(pattern))
    return files


def _discover_from_payload(payload: dict[str, Any], path: Path) -> list[DiscoveredHost]:
    routers = (((payload.get("http") or {}).get("routers")) or {})
    if not isinstance(routers, dict):
        return []

    discovered: list[DiscoveredHost] = []
    for router_name, router in routers.items():
        if not isinstance(router, dict):
            continue
        rule = router.get("rule")
        if not isinstance(rule, str):
            continue
        service_name = router.get("service") if isinstance(router.get("service"), str) else None

        for parsed in parse_host_rules(rule):
            discovered.append(
                DiscoveredHost(
                    host=parsed.host,
                    source=str(path),
                    source_type="file_provider",
                    source_file=str(path),
                    service_name=service_name,
                    router_name=str(router_name),
                    rule=rule,
                    rule_type=parsed.rule_type,
                    regex_based=parsed.regex_based,
                    notes="HostRegexp requires review before use as a plain DNS target."
                    if parsed.regex_based
                    else None,
                )
            )

    return discovered
