# Usage

Run directly from the repo:

```bash
git clone https://github.com/worryboy/traefik-domain-discovery.git
cd traefik-domain-discovery
./traefik-domain-discover --docker --traefik-api http://127.0.0.1:8080/api/rawdata
```

Primary command:

```bash
./traefik-domain-discover --docker --traefik-api http://127.0.0.1:8080/api/rawdata
```

More complete example:

```bash
./traefik-domain-discover \
  --docker \
  --traefik-api http://127.0.0.1:8080/api/rawdata \
  --file-provider-dir /path/to/traefik/dynamic \
  --zone-overrides examples/zone-overrides.example.yaml \
  --access-log /var/log/traefik/access.log \
  --output /tmp/traefik-domain-discovery/discovered-hosts.yaml \
  --json-output /tmp/traefik-domain-discovery/discovered-hosts.json \
  --selection-template /tmp/traefik-domain-discovery/selected-targets.yaml
```

Sample config only:

```bash
./traefik-domain-discover \
  --file-provider-dir examples \
  --output /tmp/discovered-hosts.yaml
```

Default output is compact and intended for human review:

```yaml
hosts:
  - host: app.example.com
    zone: example.com
    dns_provider: manual
    sources:
      - type: file_provider
        service: app-service
        file: examples/config.example.yaml
```

Zone detection is best effort and intentionally lightweight. DNS provider values are manual review data from `--zone-overrides`, not automatic guesses.

Without `--output`, the default file goes to `/tmp/traefik-domain-discovery/discovered-hosts.yaml` on a typical Linux host.
