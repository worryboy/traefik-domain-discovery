from __future__ import annotations

import shutil
import subprocess

from .models import DiscoveredHost


COMMON_PUBLIC_SUFFIXES = {
    "ac.uk",
    "co.at",
    "co.jp",
    "co.nz",
    "co.uk",
    "com.au",
    "com.br",
    "com.tr",
    "com.ua",
    "com.pl",
    "com.sg",
    "com.mx",
    "edu.au",
    "gov.uk",
    "net.au",
    "net.nz",
    "org.au",
    "org.uk",
}


PROVIDER_HINTS = {
    "cloudflare": "cloudflare",
    "awsdns": "route53",
    "route53": "route53",
    "digitalocean": "digitalocean",
    "hetzner": "hetzner",
    "your-server.de": "hetzner",
    "ionos": "ionos",
    "ui-dns": "ionos",
    "stratoserver": "strato",
    "rzone": "strato",
    "netcup": "netcup",
    "godaddy": "godaddy",
    "domaincontrol": "godaddy",
    "namecheap": "namecheap",
    "registrar-servers": "namecheap",
    "infomaniak": "infomaniak",
    "ovh": "ovh",
    "dnsimple": "dnsimple",
    "dnsmadeeasy": "dnsmadeeasy",
    "azure-dns": "azure",
    "googledomains": "google",
    "google.com": "google",
    "gandi": "gandi",
    "porkbun": "porkbun",
    "vercel-dns": "vercel",
    "internetx": "internetx",
    "ns14.net": "internetx",
    "ns15.net": "internetx",
    "ns16.net": "internetx",
    "ns17.net": "internetx",
}


def enrich_with_dns_metadata(hosts: list[DiscoveredHost], guess_provider: bool = False) -> list[DiscoveredHost]:
    zones = {host.zone or detect_zone(host.host) for host in hosts}
    zones.discard(None)
    provider_guesses = {
        zone: guess_dns_provider(zone)
        for zone in sorted(zones)
        if guess_provider and zone is not None
    }

    for host in hosts:
        host.zone = host.zone or detect_zone(host.host)
        if not host.zone or host.zone not in provider_guesses:
            continue

        guess = provider_guesses[host.zone]
        if guess is None:
            continue
        provider, confidence, source = guess
        host.dns_provider_guess = provider
        host.dns_provider_confidence = confidence
        host.provider_detection_source = source

    return hosts


def detect_zone(hostname: str) -> str | None:
    labels = _usable_labels(hostname)
    if len(labels) < 2:
        return None

    suffix = ".".join(labels[-2:])
    if suffix in COMMON_PUBLIC_SUFFIXES and len(labels) >= 3:
        return ".".join(labels[-3:])
    return suffix


def guess_dns_provider(zone: str) -> tuple[str, str, str] | None:
    nameservers = lookup_nameservers(zone)
    if not nameservers:
        return None

    for nameserver in nameservers:
        normalized = nameserver.lower().rstrip(".")
        for hint, provider in PROVIDER_HINTS.items():
            if hint in normalized:
                return provider, "medium", "nameserver"

    return None


def lookup_nameservers(zone: str) -> list[str]:
    if shutil.which("dig"):
        return _lookup_with_dig(zone)
    if shutil.which("host"):
        return _lookup_with_host(zone)
    if shutil.which("nslookup"):
        return _lookup_with_nslookup(zone)
    return []


def _lookup_with_dig(zone: str) -> list[str]:
    completed = _run_dns_command(["dig", "+short", "NS", zone])
    return [line.strip() for line in completed.splitlines() if line.strip()]


def _lookup_with_host(zone: str) -> list[str]:
    completed = _run_dns_command(["host", "-t", "NS", zone])
    nameservers: list[str] = []
    for line in completed.splitlines():
        if " name server " not in line:
            continue
        nameservers.append(line.rsplit(" name server ", 1)[1].strip())
    return nameservers


def _lookup_with_nslookup(zone: str) -> list[str]:
    completed = _run_dns_command(["nslookup", "-type=NS", zone])
    nameservers: list[str] = []
    for line in completed.splitlines():
        if "nameserver =" in line:
            nameservers.append(line.rsplit("nameserver =", 1)[1].strip())
    return nameservers


def _run_dns_command(command: list[str]) -> str:
    try:
        completed = subprocess.run(
            command,
            check=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired):
        return ""
    if completed.returncode != 0:
        return ""
    return completed.stdout


def _usable_labels(hostname: str) -> list[str]:
    labels: list[str] = []
    for raw_label in hostname.strip(".").lower().split("."):
        label = raw_label.strip()
        if not label or label == "*":
            continue
        if "{" in label or "}" in label or ":" in label:
            continue
        labels.append(label)
    return labels
