from __future__ import annotations

import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import urlopen

from .models import DiscoveredHost
from .traefik_rules import parse_host_rules


def discover_from_traefik_api(api_url: str) -> list[DiscoveredHost]:
    payload = _read_json(api_url)
    routers, api_view = _extract_routers(payload, api_url)
    source = _source_label(api_url)

    discovered: list[DiscoveredHost] = []
    for router in routers:
        rule = router.get("rule")
        if not isinstance(rule, str):
            continue

        provider = _provider_name(router)
        service_name = router.get("service") if isinstance(router.get("service"), str) else None

        for parsed in parse_host_rules(rule):
            discovered.append(
                DiscoveredHost(
                    host=parsed.host,
                    source=source,
                    source_type="traefik_api",
                    service_name=service_name,
                    rule=rule,
                    rule_type=parsed.rule_type,
                    regex_based=parsed.regex_based,
                    provider=provider,
                    api_view=api_view,
                    notes="HostRegexp requires review before use as a plain DNS target."
                    if parsed.regex_based
                    else None,
                )
            )

    return discovered


def _read_json(api_url: str) -> Any:
    try:
        with urlopen(api_url, timeout=10) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return json.loads(response.read().decode(charset))
    except HTTPError as exc:
        raise RuntimeError(f"Traefik API request failed with HTTP {exc.code}: {api_url}") from exc
    except URLError as exc:
        raise RuntimeError(f"Traefik API request failed for {api_url}: {exc.reason}") from exc
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"Traefik API response was not valid JSON: {api_url}") from exc


def _extract_routers(payload: Any, api_url: str) -> tuple[list[dict[str, Any]], str]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)], "http_routers"

    if not isinstance(payload, dict):
        raise RuntimeError(f"Traefik API returned an unexpected payload type for {api_url}")

    rawdata_routers = payload.get("routers")
    if isinstance(rawdata_routers, dict):
        return [
            _normalize_rawdata_router(name, router)
            for name, router in rawdata_routers.items()
            if isinstance(router, dict)
        ], "rawdata"

    http_routers = ((payload.get("http") or {}).get("routers")) if isinstance(payload.get("http"), dict) else None
    if isinstance(http_routers, dict):
        return [
            _normalize_rawdata_router(name, router)
            for name, router in http_routers.items()
            if isinstance(router, dict)
        ], "http_routers_map"

    raise RuntimeError(
        "Traefik API payload did not contain a supported router view. "
        "Use /api/http/routers or /api/rawdata."
    )


def _normalize_rawdata_router(name: str, router: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(router)
    normalized.setdefault("name", name)
    return normalized


def _source_label(api_url: str) -> str:
    parsed = urlparse(api_url)
    if parsed.netloc:
        return parsed.netloc
    return api_url


def _provider_name(router: dict[str, Any]) -> str | None:
    provider = router.get("provider")
    if isinstance(provider, str) and provider:
        return provider

    name = router.get("name")
    if isinstance(name, str) and "@" in name:
        return name.rsplit("@", 1)[1]

    return None
