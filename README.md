# traefik-domain-discovery

Small Python CLI for discovering Traefik hostnames from a live Docker + Traefik setup and exporting a reviewable list for later DNS selection.

It does:

- inspect running Docker containers for Traefik router rules
- optionally read Traefik file-provider config
- optionally mark discovered hosts as seen in access logs
- export reviewable YAML and JSON

It does not:

- update DNS
- call DNS provider APIs
- decide automatically which hosts should become public DNS targets

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Optional, for fuller YAML support:

```bash
python -m pip install -e ".[yaml]"
```

## Usage

Primary command:

```bash
traefik-domain-discover discover --docker --output discovered-hosts.yaml
```

With file-provider config and access-log enrichment:

```bash
traefik-domain-discover discover \
  --docker \
  --file-provider-dir /path/to/traefik/dynamic \
  --access-log /var/log/traefik/access.log \
  --output discovered-hosts.yaml \
  --json-output discovered-hosts.json \
  --selection-template selected-targets.yaml
```

Quick local example with the included sample config:

```bash
traefik-domain-discover discover \
  --file-provider-dir examples \
  --output /tmp/discovered-hosts.yaml \
  --json-output /tmp/discovered-hosts.json
```

## Output

The main output is a deduplicated list of discovered hosts with review metadata such as:

- `host`
- `source`
- `source_type`
- `container_name`
- `service_name`
- `compose_project`
- `router_name`
- `seen_in_access_log`
- `selected`
- `notes`

`HostRegexp(...)` rules are kept, but marked as regex-based so they can be reviewed separately.

## License

MIT
