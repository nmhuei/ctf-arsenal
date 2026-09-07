#!/usr/bin/env python3
"""Minimal read-only Gitea API facade used for migration-path probing."""

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from urllib.parse import urlparse


TARGET_CLONE = os.environ["TARGET_CLONE"]


class Handler(BaseHTTPRequestHandler):
    server_version = "Gitea/1.22.0"

    def log_message(self, fmt, *args):
        print(fmt % args, flush=True)

    def send_json(self, value, status=200):
        payload = json.dumps(value).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/api/v1/version":
            return self.send_json({"version": "1.22.0"})
        if path == "/api/v1/settings/api":
            return self.send_json({"max_response_items": 10})
        if path == "/api/v1/repos/evil/source":
            return self.send_json({
                "id": 1,
                "name": "source",
                "full_name": "evil/source",
                "description": "migration source",
                "private": False,
                "empty": False,
                "default_branch": "main",
                "clone_url": TARGET_CLONE,
                "owner": {"id": 1, "login": "evil", "username": "evil"},
            })
        if path == "/api/v1/repos/evil/source/topics":
            return self.send_json({"topics": []})
        if path == "/api/v1/repos/evil/source/releases":
            return self.send_json([{
                "id": 1,
                "tag_name": "v1.0.0",
                "target_commitish": "main",
                "name": "probe",
                "body": "",
                "draft": False,
                "prerelease": False,
                "created_at": "2026-01-01T00:00:00Z",
                "published_at": "2026-01-01T00:00:00Z",
                "publisher": {"id": 1, "login": "evil", "username": "evil", "email": "evil@example.invalid"},
                "assets": [{
                    "id": 1,
                    "name": "flag.txt",
                    "size": 128,
                    "download_count": 0,
                    "created_at": "2026-01-01T00:00:00Z",
                    "browser_download_url": "file:///flag.txt",
                }],
            }])
        if path == "/api/v1/repos/evil/source/releases/1/assets/1":
            return self.send_json({
                "id": 1,
                "name": "flag.txt",
                "size": 128,
                "download_count": 0,
                "browser_download_url": "file:///flag.txt",
                "type": "external",
            })
        if path.startswith("/api/v1/repos/evil/source/"):
            return self.send_json([])
        return self.send_json({"message": "not found"}, 404)


if __name__ == "__main__":
    port = int(os.environ.get("FAKE_PORT", "18080"))
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()
