from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from .access_log import enrich_with_access_log, read_seen_hosts
from .docker_discovery import discover_from_docker
from .exporters import export_hosts, export_selection_template
from .file_provider import discover_from_file_provider
from .models import DiscoveredHost, merge_hosts

DEFAULT_OUTPUT_PATH = Path(tempfile.gettempdir()) / "traefik-domain-discovery" / "discovered-hosts.yaml"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="traefik-domain-discover",
        description="Discover Traefik hostnames for review before Dynamic DNS target selection.",
    )
    parser.add_argument("--docker", action="store_true", help="inspect running Docker containers")
    parser.add_argument("--file-provider-dir", help="read Traefik dynamic YAML config from this directory")
    parser.add_argument("--access-log", help="read Traefik JSON access log and mark discovered hosts as seen")
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT_PATH),
        help="write discovered hosts as YAML or JSON based on extension",
    )
    parser.add_argument(
        "--json-output",
        help="also write a JSON export to this path",
    )
    parser.add_argument(
        "--selection-template",
        help="write a reviewable selected-targets YAML template",
    )

    return parser


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]
    if argv and argv[0] == "discover":
        argv = argv[1:]

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        hosts = run_discovery(args)
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    output_path = export_hosts(hosts, args.output)
    print(f"wrote {len(hosts)} discovered host entries to {output_path}")

    if args.json_output:
        json_path = export_hosts(hosts, args.json_output)
        print(f"wrote JSON export to {json_path}")

    if args.selection_template:
        selection_path = export_selection_template(hosts, args.selection_template)
        print(f"wrote selection template to {selection_path}")

    return 0


def run_discovery(args: argparse.Namespace) -> list[DiscoveredHost]:
    if not args.docker and not args.file_provider_dir:
        raise ValueError("choose at least one discovery source: --docker or --file-provider-dir")

    discovered: list[DiscoveredHost] = []

    if args.docker:
        discovered.extend(discover_from_docker())

    if args.file_provider_dir:
        discovered.extend(discover_from_file_provider(Path(args.file_provider_dir)))

    merged = merge_hosts(discovered)

    if args.access_log:
        seen_hosts = read_seen_hosts(Path(args.access_log))
        enrich_with_access_log(merged, seen_hosts)

    return merged


if __name__ == "__main__":
    raise SystemExit(main())
