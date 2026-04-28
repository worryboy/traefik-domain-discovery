# Architecture

`traefik-domain-discovery` is intentionally a discovery and export tool. It does not update DNS records and does not contain DNS provider API code.

## Discovery Sources

The MVP supports three signals:

- Docker labels from currently running containers, especially `traefik.http.routers.*.rule`
- Traefik dynamic file-provider YAML config, when a directory is supplied
- Traefik JSON access logs, when a log path is supplied

Docker labels are the primary source because many real Traefik deployments define routers through container labels rather than static files.

## Rule Parsing

The parser extracts arguments from:

- `Host(...)`
- `HostRegexp(...)`

`Host(...)` entries are treated as plain host candidates. `HostRegexp(...)` entries are preserved, but marked as regex-based because they are not automatically safe to use as direct DNS targets.

## Deduplication

Discovered entries are deduplicated by normalized host value and rule type. The first source remains the primary source, and additional sources are retained under `extra_sources` so review metadata is not lost.

## Access Logs

Access logs are enrichment only. A hostname seen in logs may be useful evidence that a route is active, but logs are not complete inventory:

- quiet services may not appear
- retention may be short
- bots and invalid requests may create noise
- internal-only routes may never be logged externally

For that reason, logs only set `seen_in_access_log` on already discovered hostnames.

## Review Before Dynamic DNS

Not every Traefik hostname should become a Dynamic DNS target. Some names may be internal, temporary, delegated elsewhere, covered by wildcard DNS, or intentionally not public.

The selection template is deliberately disabled by default. A future DNS updater can consume a reviewed target file, but this project stops at discovery and preparation.
