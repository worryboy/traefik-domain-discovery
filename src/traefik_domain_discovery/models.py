from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


@dataclass(slots=True)
class DiscoveredHost:
    host: str
    source: str
    source_type: str
    container_name: str | None = None
    service_name: str | None = None
    compose_project: str | None = None
    router_name: str | None = None
    router_label_key: str | None = None
    source_file: str | None = None
    rule: str | None = None
    rule_type: str = "host"
    regex_based: bool = False
    seen_in_access_log: bool = False
    selected: bool = False
    enabled: bool = False
    dns_provider: str | None = None
    zone: str | None = None
    target_type: str | None = None
    notes: str | None = None
    extra_sources: list[dict[str, Any]] = field(default_factory=list)

    def dedupe_key(self) -> tuple[str, str]:
        return (self.host.lower(), self.rule_type)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        return {key: value for key, value in data.items() if value not in (None, [], {})}


def merge_hosts(hosts: list[DiscoveredHost]) -> list[DiscoveredHost]:
    merged: dict[tuple[str, str], DiscoveredHost] = {}

    for host in hosts:
        key = host.dedupe_key()
        existing = merged.get(key)
        if existing is None:
            merged[key] = host
            continue

        existing.seen_in_access_log = existing.seen_in_access_log or host.seen_in_access_log
        if existing.notes and host.notes and host.notes not in existing.notes:
            existing.notes = f"{existing.notes}; {host.notes}"
        elif host.notes and not existing.notes:
            existing.notes = host.notes

        existing.extra_sources.append(
            {
                "source": host.source,
                "source_type": host.source_type,
                "container_name": host.container_name,
                "service_name": host.service_name,
                "compose_project": host.compose_project,
                "router_name": host.router_name,
                "router_label_key": host.router_label_key,
                "source_file": host.source_file,
                "rule": host.rule,
            }
        )

    return sorted(merged.values(), key=lambda item: (item.host.lower(), item.source_type, item.source))

