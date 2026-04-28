from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import urlparse

from .models import DiscoveredHost


HOST_FIELDS = ("RequestHost", "requestHost", "Host", "host")
URL_FIELDS = ("RequestURL", "requestURL", "DownstreamRequestURL")


def read_seen_hosts(log_path: str | Path) -> set[str]:
    path = Path(log_path).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"access log does not exist: {path}")

    seen: set[str] = set()
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            host = _host_from_record(record)
            if host:
                seen.add(_normalize_host(host))

    return seen


def enrich_with_access_log(hosts: list[DiscoveredHost], seen_hosts: set[str]) -> list[DiscoveredHost]:
    normalized_seen = {_normalize_host(host) for host in seen_hosts}
    for host in hosts:
        host.seen_in_access_log = _normalize_host(host.host) in normalized_seen
    return hosts


def _host_from_record(record: dict[str, object]) -> str | None:
    for field in HOST_FIELDS:
        value = record.get(field)
        if isinstance(value, str) and value.strip():
            return value

    for field in URL_FIELDS:
        value = record.get(field)
        if not isinstance(value, str) or not value.strip():
            continue
        parsed = urlparse(value)
        if parsed.netloc:
            return parsed.netloc

    return None


def _normalize_host(host: str) -> str:
    return host.strip().lower().split(":", 1)[0]

