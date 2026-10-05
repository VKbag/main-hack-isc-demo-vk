"""Build Delimited File account schema attributes from a CSV header row."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import Any

# Attributes that should be typed as boolean in account schema
BOOLEAN_ATTRS = {
    "TERMINATED",
    "ACTIVE",
    "REHIRE",
    "ON_LEAVE",
    "IS_RESCINDED",
    "TERMINATION_INVOLUNTARY",
}


def read_csv_headers(csv_path: str | Path) -> list[str]:
    path = Path(csv_path)
    if not path.is_file():
        raise FileNotFoundError(f"CSV not found: {path}")
    with path.open(newline="", encoding="utf-8-sig") as fh:
        reader = csv.reader(fh)
        headers = next(reader, None)
    if not headers:
        raise ValueError(f"No header row in {path}")
    return [h.strip() for h in headers if h and h.strip()]


def build_account_schema_attributes(headers: list[str]) -> list[dict[str, Any]]:
    """Build schema attributes. ISC expects type STRING|BOOLEAN|LONG|INT (uppercase)."""
    attrs: list[dict[str, Any]] = []
    for name in headers:
        attrs.append(
            {
                "name": name,
                "type": "BOOLEAN" if name.upper() in BOOLEAN_ATTRS else "STRING",
                "description": name,
                "isMulti": False,
                "isEntitlement": False,
                "isGroup": False,
            }
        )
    return attrs


def schema_payload_from_csv(csv_path: str | Path) -> dict[str, Any]:
    if not csv_path:
        raise ValueError("csv_path is required")
    headers = read_csv_headers(csv_path)
    path = Path(csv_path)
    # Prefer common HR id columns when present; else first header.
    identity_attr = "WORKER_ID" if "WORKER_ID" in headers else headers[0]
    display_attr = identity_attr
    return {
        "name": "account",
        "nativeObjectType": "User",
        "identityAttribute": identity_attr,
        "displayAttribute": display_attr,
        "attributes": build_account_schema_attributes(headers),
        "headers": headers,
        "csv_path": str(path),
    }
