from __future__ import annotations

import re
from dataclasses import dataclass


HOST_CALL_RE = re.compile(r"\b(Host|HostRegexp)\s*\((.*?)\)", re.IGNORECASE | re.DOTALL)
QUOTED_VALUE_RE = re.compile(r"`([^`]+)`|'([^']+)'|\"([^\"]+)\"")


@dataclass(frozen=True, slots=True)
class ParsedHostRule:
    host: str
    rule_type: str
    regex_based: bool


def parse_host_rules(rule: str) -> list[ParsedHostRule]:
    """Extract Host(...) and HostRegexp(...) arguments from a Traefik rule."""
    results: list[ParsedHostRule] = []

    for match in HOST_CALL_RE.finditer(rule or ""):
        call_name = match.group(1).lower()
        args = match.group(2)
        regex_based = call_name == "hostregexp"
        rule_type = "hostregexp" if regex_based else "host"

        for quoted in QUOTED_VALUE_RE.findall(args):
            value = next(part for part in quoted if part)
            value = value.strip()
            if not value:
                continue
            results.append(ParsedHostRule(host=value, rule_type=rule_type, regex_based=regex_based))

    return results

