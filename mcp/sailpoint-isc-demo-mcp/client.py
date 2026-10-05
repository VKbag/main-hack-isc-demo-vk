"""Allowlisted SailPoint ISC demo-tenant HTTP client."""

from __future__ import annotations

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv

# Hard-lock: only this demo API host (not UI host, not other tenants).
ALLOWED_API_BASE = "https://devrel-ga-25104.api.identitynow-demo.com"
DEFAULT_ENV_FILE = Path.home() / ".cursor" / "sailpoint-isc-demo.env"
AUDIT_DIR = Path(__file__).resolve().parent / ".audit"


class DemoGuardError(RuntimeError):
    """Raised when a non-demo host or unsafe config is detected."""


def _ca_bundle() -> str | bool:
    for var in ("SAILPOINT_CA_BUNDLE", "REQUESTS_CA_BUNDLE", "SSL_CERT_FILE"):
        path = os.environ.get(var)
        if path and Path(path).is_file():
            return path
    return True


def _normalize_base(url: str) -> str:
    return url.rstrip("/")


def load_demo_env() -> dict[str, str]:
    env_file = Path(os.environ.get("SAILPOINT_DEMO_ENV_FILE", DEFAULT_ENV_FILE))
    local_env = Path(__file__).resolve().parent / ".env"
    if env_file.is_file():
        load_dotenv(env_file, override=False)
    elif local_env.is_file():
        load_dotenv(local_env, override=False)

    api_base = _normalize_base(os.environ.get("SAILPOINT_API_BASE", ALLOWED_API_BASE))
    client_id = os.environ.get("SAILPOINT_CLIENT_ID", "").strip()
    client_secret = os.environ.get("SAILPOINT_CLIENT_SECRET", "").strip()
    token_url = os.environ.get("SAILPOINT_TOKEN_URL", f"{api_base}/oauth/token").strip()
    api_version = os.environ.get("SAILPOINT_API_VERSION", "v2024").strip()

    if api_base != ALLOWED_API_BASE:
        raise DemoGuardError(
            f"Refusing API base {api_base!r}. Only {ALLOWED_API_BASE!r} is allowed."
        )

    token_host = _normalize_base(
        f"{urlparse(token_url).scheme}://{urlparse(token_url).netloc}"
    )
    if token_host != ALLOWED_API_BASE:
        raise DemoGuardError(
            f"Refusing token URL host {token_host!r}. Only {ALLOWED_API_BASE!r} is allowed."
        )

    if not client_id or not client_secret:
        raise DemoGuardError(
            "Missing SAILPOINT_CLIENT_ID / SAILPOINT_CLIENT_SECRET. "
            f"Create {env_file} from .env.example (demo PAT only)."
        )

    return {
        "api_base": api_base,
        "client_id": client_id,
        "client_secret": client_secret,
        "token_url": token_url,
        "api_version": api_version,
    }


class SailPointDemoClient:
    def __init__(self) -> None:
        self.cfg = load_demo_env()
        self._token: str | None = None
        self._token_expires_at = 0.0
        self._client = httpx.Client(
            timeout=120.0, follow_redirects=False, verify=_ca_bundle()
        )

    def close(self) -> None:
        self._client.close()

    def _assert_url(self, url: str) -> None:
        parsed = urlparse(url)
        host_base = _normalize_base(f"{parsed.scheme}://{parsed.netloc}")
        if host_base != ALLOWED_API_BASE:
            raise DemoGuardError(
                f"Blocked non-demo URL {url!r}. Allowed host: {ALLOWED_API_BASE}"
            )

    def _audit(
        self,
        tool: str,
        method: str,
        path: str,
        status: int | None,
        extra: dict | None = None,
    ) -> None:
        AUDIT_DIR.mkdir(parents=True, exist_ok=True)
        day = datetime.now(timezone.utc).strftime("%Y%m%d")
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "tool": tool,
            "method": method,
            "path": path,
            "status": status,
            "extra": extra or {},
        }
        with (AUDIT_DIR / f"{day}.jsonl").open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(record, default=str) + "\n")

    def _get_token(self) -> str:
        now = time.time()
        if self._token and now < self._token_expires_at - 60:
            return self._token

        self._assert_url(self.cfg["token_url"])
        resp = self._client.post(
            self.cfg["token_url"],
            data={"grant_type": "client_credentials"},
            auth=(self.cfg["client_id"], self.cfg["client_secret"]),
            headers={"Accept": "application/json"},
        )
        if resp.status_code >= 400:
            raise RuntimeError(
                f"OAuth token request failed ({resp.status_code}): {resp.text[:500]}"
            )
        payload = resp.json()
        self._token = payload["access_token"]
        self._token_expires_at = now + float(payload.get("expires_in", 3600))
        return self._token

    def url(self, path: str, version: str | None = None) -> str:
        ver = version or self.cfg["api_version"]
        if path.startswith("http"):
            self._assert_url(path)
            return path
        if not path.startswith("/"):
            path = "/" + path
        if path.startswith("/v") or path.startswith("/beta"):
            return f"{self.cfg['api_base']}{path}"
        return f"{self.cfg['api_base']}/{ver}{path}"

    def request(
        self,
        method: str,
        path: str,
        *,
        tool: str = "unknown",
        version: str | None = None,
        params: dict | None = None,
        json_body: Any = None,
        headers: dict | None = None,
        expected: tuple[int, ...] = (200, 201, 202, 204),
    ) -> Any:
        url = self.url(path, version=version)
        self._assert_url(url)
        token = self._get_token()
        hdrs = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }
        if json_body is not None:
            hdrs["Content-Type"] = "application/json"
        if headers:
            hdrs.update(headers)

        resp = self._client.request(
            method, url, params=params, json=json_body, headers=hdrs
        )
        if resp.status_code in (301, 302, 303, 307, 308):
            loc = resp.headers.get("location", "")
            self._assert_url(loc)
            raise DemoGuardError(f"Redirect to {loc} blocked/unsupported; use final URL.")

        self._audit(tool, method, path, resp.status_code)

        if resp.status_code not in expected:
            raise RuntimeError(
                f"{method} {path} failed ({resp.status_code}): {resp.text[:2000]}"
            )
        if resp.status_code == 204 or not resp.content:
            return None
        ctype = resp.headers.get("content-type", "")
        if "application/json" in ctype:
            return resp.json()
        return resp.text

    def get(self, path: str, **kwargs: Any) -> Any:
        return self.request("GET", path, **kwargs)

    def post(self, path: str, **kwargs: Any) -> Any:
        return self.request("POST", path, **kwargs)


_client: SailPointDemoClient | None = None


def get_client() -> SailPointDemoClient:
    global _client
    if _client is None:
        _client = SailPointDemoClient()
    return _client


def ok(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


def err(exc: Exception) -> str:
    return json.dumps({"error": type(exc).__name__, "message": str(exc)}, indent=2)
