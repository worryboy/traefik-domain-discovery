# traefik-domain-discovery

A small Python CLI that discovers Traefik hostnames from a Docker + Traefik environment and exports a reviewable inventory for later Dynamic DNS target selection.

This is **not** a DNS updater. It does not call DNS provider APIs, change records, or apply live Dynamic DNS updates.

## Why This Exists

In many practical Traefik setups, hostnames are not all defined in one static file. Docker containers often create routers dynamically through labels such as:

```text
traefik.http.routers.app.rule=Host(`app.example.com`)
```

That means a useful Dynamic DNS workflow needs a discovery step that inspects the real running Docker and Traefik landscape before any DNS target list is chosen.

This project focuses on that first step: discovery, inventory, metadata, deduplication, and export preparation.

## What It Does

- inspects currently running Docker containers
- extracts Traefik router rules from labels like `traefik.http.routers.*.rule`
- parses `Host(...)` rules into plain hostname candidates
- captures `HostRegexp(...)` separately and marks it as regex-based
- optionally reads Traefik dynamic file-provider YAML config
- optionally reads Traefik JSON access logs to mark discovered hosts as seen
- exports reviewable YAML and JSON
- can generate a disabled selection template for later Dynamic DNS work

## What It Does Not Do

- no live DNS updates
- no DNS provider credentials
- no provider API logic
- no automatic decision that a hostname should be public
- no heavy UI or framework

The review step is intentional. Not every Traefik hostname should become a Dynamic DNS target.

## Install

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

The project has no hard runtime dependencies. If you want full YAML parser support for more complex Traefik files, install the optional YAML extra:

```bash
python -m pip install -e ".[yaml]"
```

## Examples

Discover from Docker labels only:

```bash
traefik-domain-discover discover \
  --docker \
  --output discovered-hosts.yaml
```

Discover from Docker labels and a Traefik file-provider directory:

```bash
traefik-domain-discover discover \
  --docker \
  --file-provider-dir /path/to/traefik/dynamic \
  --output discovered-hosts.yaml \
  --json-output discovered-hosts.json
```

Discover from Docker, file-provider config, and access logs:

```bash
traefik-domain-discover discover \
  --docker \
  --file-provider-dir /path/to/traefik/dynamic \
  --access-log /var/log/traefik/access.log \
  --output discovered-hosts.yaml \
  --json-output discovered-hosts.json \
  --selection-template selected-targets.yaml
```

Try the included example config without Docker:

```bash
traefik-domain-discover discover \
  --file-provider-dir examples \
  --output /tmp/discovered-hosts.yaml \
  --json-output /tmp/discovered-hosts.json \
  --selection-template /tmp/selected-targets.yaml
```

## Output Model

Exports include fields such as:

- `host`
- `source`
- `source_type`
- `container_name`
- `service_name`
- `compose_project`
- `router_name`
- `router_label_key`
- `source_file`
- `rule`
- `rule_type`
- `regex_based`
- `seen_in_access_log`
- `selected`
- `enabled`
- `dns_provider`
- `zone`
- `target_type`
- `notes`

Future DNS tooling can use the reviewed selection file, but this project deliberately stops before applying anything.

## HostRegexp Handling

`HostRegexp(...)` rules are preserved because they are operationally useful, but they are marked as regex-based and excluded from the generated selection template. A regex rule is not automatically a concrete DNS target.

## Suggested Repository Metadata

Description:

```text
Discover Traefik hostnames from Docker labels, file-provider config, and access logs for reviewable Dynamic DNS target preparation.
```

Topics:

```text
docker, traefik, dynamic-dns, discovery, homelab, self-hosted, devops
```

## Suggested First Git Commands

```bash
git init
git add .
git commit -m "Initial Traefik domain discovery MVP"
git branch -M main
git remote add origin git@github.com:YOUR_USER/traefik-domain-discovery.git
git push -u origin main
```

## License

MIT
