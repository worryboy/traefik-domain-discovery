# traefik-domain-discovery

Small Python CLI for discovering Traefik hostnames from a live Docker + Traefik setup and exporting a reviewable list for later DNS selection.

It does:

- inspect running Docker containers for Traefik router rules
- optionally read active routers from the Traefik API
- optionally read Traefik file-provider config
- optionally mark discovered hosts as seen in access logs
- export reviewable YAML and JSON

It does not:

- update DNS
- call DNS provider APIs
- decide automatically which hosts should become public DNS targets

## Run

```bash
git clone https://github.com/worryboy/traefik-domain-discovery.git
cd traefik-domain-discovery
./traefik-domain-discover --docker --traefik-api http://127.0.0.1:8080/api/rawdata
```

No fixed install path is required. Copy or clone the repo anywhere and run it directly with `python3`.

Optional, for fuller YAML support if your host does not already have PyYAML:

```bash
python3 -m pip install --user PyYAML
```

## Usage

Primary command:

```bash
./traefik-domain-discover --docker --traefik-api http://127.0.0.1:8080/api/rawdata
```

With file-provider config and access-log enrichment:

```bash
./traefik-domain-discover \
  --docker \
  --traefik-api http://127.0.0.1:8080/api/rawdata \
  --file-provider-dir /path/to/traefik/dynamic \
  --access-log /var/log/traefik/access.log \
  --output /tmp/traefik-domain-discovery/discovered-hosts.yaml \
  --json-output /tmp/traefik-domain-discovery/discovered-hosts.json \
  --selection-template /tmp/traefik-domain-discovery/selected-targets.yaml
```

Quick local example with the included sample config:

```bash
./traefik-domain-discover \
  --file-provider-dir examples \
  --output /tmp/discovered-hosts.yaml \
  --json-output /tmp/discovered-hosts.json
```

## Output

The main output is a compact, deduplicated review file. Each host is listed alphabetically with a short `sources` list showing where it came from:

```yaml
hosts:
  - host: app.example.com
    seen_in_access_log: true
    sources:
      - type: docker_label
        container: web
        service: app
        project: homelab
      - type: file_provider
        service: app-service
        file: dynamic.yaml
```

`HostRegexp(...)` rules are kept and include a short review note, but router names, rule text, label keys, and selection flags are not included in the default discovery output.

When the Traefik API is available, `--docker` plus `--traefik-api` is the preferred practical path. File-provider parsing stays optional.

If you do not pass `--output`, the default file is written to `/tmp/traefik-domain-discovery/discovered-hosts.yaml` on a typical Linux host.

## License

MIT
