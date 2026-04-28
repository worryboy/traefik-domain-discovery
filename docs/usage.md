# Usage

Install:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
```

Primary command:

```bash
traefik-domain-discover discover --docker --output discovered-hosts.yaml
```

More complete example:

```bash
traefik-domain-discover discover \
  --docker \
  --file-provider-dir /path/to/traefik/dynamic \
  --access-log /var/log/traefik/access.log \
  --output discovered-hosts.yaml \
  --json-output discovered-hosts.json \
  --selection-template selected-targets.yaml
```

Sample config only:

```bash
traefik-domain-discover discover \
  --file-provider-dir examples \
  --output /tmp/discovered-hosts.yaml
```
