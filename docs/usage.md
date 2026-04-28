# Usage

Install locally during development:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Discover from running Docker containers:

```bash
traefik-domain-discover discover --docker --output discovered-hosts.yaml
```

Discover from Docker and a Traefik file-provider directory:

```bash
traefik-domain-discover discover \
  --docker \
  --file-provider-dir /path/to/traefik/dynamic \
  --output discovered-hosts.yaml \
  --json-output discovered-hosts.json
```

Add access-log enrichment:

```bash
traefik-domain-discover discover \
  --docker \
  --file-provider-dir /path/to/traefik/dynamic \
  --access-log /var/log/traefik/access.log \
  --output discovered-hosts.yaml \
  --selection-template selected-targets.yaml
```

Run only against the included example file-provider config:

```bash
traefik-domain-discover discover \
  --file-provider-dir examples \
  --output /tmp/discovered-hosts.yaml \
  --json-output /tmp/discovered-hosts.json \
  --selection-template /tmp/selected-targets.yaml
```
