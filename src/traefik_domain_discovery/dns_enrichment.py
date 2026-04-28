from __future__ import annotations

from pathlib import Path
from typing import Any

from . import yaml_compat as yaml
from .models import DiscoveredHost


COMMON_PUBLIC_SUFFIXES = {
    "ac.uk",
    "co.at",
    "co.jp",
    "co.nz",
    "co.uk",
    "com.au",
    "com.br",
    "com.tr",
    "com.ua",
    "com.pl",
    "com.sg",
    "com.mx",
    "edu.au",
    "gov.uk",
    "net.au",
    "net.nz",
    "org.au",
    "org.uk",
}


def enrich_with_dns_metadata(
    hosts: list[DiscoveredHost],
    zone_overrides: dict[str, dict[str, str]] | None = None,
) -> list[DiscoveredHost]:
    normalized_overrides = _normalize_zone_overrides(zone_overrides or {})
    for host in hosts:
        host.zone = host.zone or detect_zone(host.host)
        if not host.zone:
            continue

        override = normalized_overrides.get(host.zone.lower())
        if override and override.get("dns_provider"):
            host.dns_provider = override["dns_provider"]

    return hosts


def load_zone_overrides(path: str | Path) -> dict[str, dict[str, str]]:
    override_path = Path(path)
    with override_path.open("r", encoding="utf-8") as handle:
        payload = yaml.safe_load(handle.read()) or {}
    if not isinstance(payload, dict):
        raise ValueError(f"zone override file must contain a mapping: {override_path}")

    raw_overrides = payload.get("zone_overrides", payload)
    if not isinstance(raw_overrides, dict):
        raise ValueError(f"zone override file must contain a zone_overrides mapping: {override_path}")

    return _normalize_zone_overrides(raw_overrides)


def detect_zone(hostname: str) -> str | None:
    labels = _usable_labels(hostname)
    if len(labels) < 2:
        return None

    suffix = ".".join(labels[-2:])
    if suffix in COMMON_PUBLIC_SUFFIXES and len(labels) >= 3:
        return ".".join(labels[-3:])
    return suffix


def _usable_labels(hostname: str) -> list[str]:
    labels: list[str] = []
    for raw_label in hostname.strip(".").lower().split("."):
        label = raw_label.strip()
        if not label or label == "*":
            continue
        if "{" in label or "}" in label or ":" in label:
            continue
        labels.append(label)
    return labels


def _normalize_zone_overrides(raw_overrides: dict[Any, Any]) -> dict[str, dict[str, str]]:
    overrides: dict[str, dict[str, str]] = {}
    for raw_zone, raw_config in raw_overrides.items():
        zone = str(raw_zone).strip(".").lower()
        if not zone:
            continue

        if isinstance(raw_config, dict):
            dns_provider = raw_config.get("dns_provider")
        else:
            dns_provider = raw_config

        if dns_provider in (None, ""):
            continue
        overrides[zone] = {"dns_provider": str(dns_provider)}
    return overrides
