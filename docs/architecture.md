# Architecture

`traefik-domain-discovery` is a discovery and export tool only. It does not update DNS.

- Primary source: Docker labels such as `traefik.http.routers.*.rule`
- Preferred active source when available: Traefik API endpoints such as `/api/rawdata` or `/api/http/routers`
- Optional source: Traefik file-provider YAML
- Optional enrichment: Traefik JSON access logs

`Host(...)` rules become plain hostname candidates. `HostRegexp(...)` rules are kept, but marked as regex-based for review.

Results are deduplicated by host and rule type. Access logs only mark whether a discovered host was seen; they are not treated as the source of truth. When the Traefik API is enabled, it is generally a better view of active routers than parsing raw files alone.

Not every Traefik hostname should become a Dynamic DNS target, so the generated selection template stays review-first and disabled by default.
