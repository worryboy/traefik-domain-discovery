from __future__ import annotations

import json
from pathlib import Path

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
                "zone": None,
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
        "hosts": [host.to_dict() for host in hosts],
    }
