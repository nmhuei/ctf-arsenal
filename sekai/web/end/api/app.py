import os
import io
import json
import hmac
from flask import Flask, request, jsonify, send_file

app = Flask(__name__)

_SECRET  = os.environ["OAUTH_SECRET"]
_API_KEY = hmac.new(_SECRET.encode(), b"api-auth", "sha256").hexdigest()[:16]
_INBOX  = [_SECRET]


@app.route("/")
def index():
    return "", 204


@app.route("/messages/search")
def search():
    if not hmac.compare_digest(request.args.get("key", ""), _API_KEY):
        return jsonify({"error": "Unauthorized"}), 401

    q = request.args.get("q", "")
    results = [m for m in _INBOX if m.startswith(q)]
    data = json.dumps({"results": results}).encode()

    return send_file(
        io.BytesIO(data),
        mimetype="application/json",
        conditional=True,
    )


_ALLOWED_HOSTS = {"api", "localhost", "127.0.0.1"}


@app.before_request
def guard():
    if request.method == "OPTIONS":
        return "", 405
    if request.host.split(":")[0] not in _ALLOWED_HOSTS:
        return "", 403
