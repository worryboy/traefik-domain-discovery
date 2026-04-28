from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from . import yaml_compat as yaml
from .models import DiscoveredHost


def export_hosts(hosts: list[DiscoveredHost], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = _document(hosts)

    if path.suffix.lower() == ".json":
        path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    return path


def export_selection_template(hosts: list[DiscoveredHost], output_path: str | Path) -> Path:
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    data = {
        "targets": [
            {
                "host": host.host,
                "enabled": False,
                "dns_provider": None,
                "zone": host.zone,
                "target_type": "A",
                "source": host.source,
                "source_type": host.source_type,
                "notes": "Review before enabling. This file is not applied automatically.",
            }
            for host in hosts
            if not host.regex_based
        ]
    }
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    return path


def _document(hosts: list[DiscoveredHost]) -> dict[str, object]:
    return {
        "schema_version": 1,
        "intent": "discovery-review-only",
        "hosts": [_compact_host(host) for host in sorted(hosts, key=lambda item: item.host.lower())],
    }


def _compact_host(host: DiscoveredHost) -> dict[str, object]:
    data: dict[str, object] = {"host": host.host}
    _copy_if_present(data, "zone", host.zone)
    _copy_if_present(data, "dns_provider_guess", host.dns_provider_guess)
    _copy_if_present(data, "dns_provider_confidence", host.dns_provider_confidence)
    _copy_if_present(data, "provider_detection_source", host.provider_detection_source)
    if host.seen_in_access_log:
        data["seen_in_access_log"] = True
    if host.notes:
        data["notes"] = host.notes

    sources = [_compact_source(_source_from_host(host))]
    sources.extend(_compact_source(source) for source in host.extra_sources)
    data["sources"] = _unique_sources(sources)
    return data


def _source_from_host(host: DiscoveredHost) -> dict[str, Any]:
    return {
        "source": host.source,
        "source_type": host.source_type,
        "container_name": host.container_name,
        "service_name": host.service_name,
        "compose_project": host.compose_project,
        "source_file": host.source_file,
        "provider": host.provider,
        "api_view": host.api_view,
    }


def _compact_source(source: dict[str, Any]) -> dict[str, object]:
    compact: dict[str, object] = {"type": source["source_type"]}
    _copy_if_present(compact, "container", source.get("container_name"))
    _copy_if_present(compact, "service", source.get("service_name"))
    _copy_if_present(compact, "project", source.get("compose_project"))

    if source.get("source_file"):
        compact["file"] = _compact_file(source["source_file"])
    elif source.get("source"):
        compact["source"] = source["source"]

    _copy_if_present(compact, "provider", source.get("provider"))
    _copy_if_present(compact, "api_view", source.get("api_view"))
    return compact


def _copy_if_present(target: dict[str, object], key: str, value: object) -> None:
    if value not in (None, "", [], {}):
        target[key] = value


def _compact_file(path_value: object) -> str:
    path = Path(str(path_value))
    if path.is_absolute():
        return path.name
    return path.as_posix()


def _unique_sources(sources: list[dict[str, object]]) -> list[dict[str, object]]:
    seen: set[tuple[tuple[str, object], ...]] = set()
    unique: list[dict[str, object]] = []
    for source in sources:
        key = tuple(source.items())
        if key in seen:
            continue
        seen.add(key)
        unique.append(source)
    return sorted(unique, key=lambda item: tuple(str(value) for value in item.values()))
