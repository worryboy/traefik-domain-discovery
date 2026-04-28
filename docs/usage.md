# Usage

Run directly from the repo:

```bash
git clone https://github.com/worryboy/traefik-domain-discovery.git
cd traefik-domain-discovery
./traefik-domain-discover --docker
```

Primary command:

```bash
./traefik-domain-discover --docker
```

More complete example:

```bash
./traefik-domain-discover \
  --docker \
  --file-provider-dir /path/to/traefik/dynamic \
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

Without `--output`, the default file goes to `/tmp/traefik-domain-discovery/discovered-hosts.yaml` on a typical Linux host.
