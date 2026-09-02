import base64
import binascii
import json

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from flask import Blueprint, current_app, g, jsonify, render_template, request, session
from werkzeug.security import generate_password_hash

from .auth import can_access, login_required, role_required, verify_login
from .crypto import decrypt, encrypt
from .db import get_db

api = Blueprint("api", __name__)


@api.get("/")
def console():
    return render_template("index.html")


def audit(action, secret_id=None, metadata=None):
    db = get_db()
    db.execute(
        "INSERT INTO audit_log(actor_id,action,secret_id,metadata,ip) VALUES(?,?,?,?,?)",
        (
            g.user["id"] if hasattr(g, "user") else None,
            action,
            secret_id,
            json.dumps(metadata or {}),
            request.remote_addr,
        ),
    )
    db.commit()


@api.get("/healthz")
def healthz():
    return {"status": "ok"}


@api.post("/api/v1/auth/login")
def login():
    body = request.get_json(silent=True) or {}
    user = verify_login(body.get("email", ""), body.get("password", ""))
    if not user:
        return jsonify(error="invalid credentials"), 401

    session.clear()
    session["user_id"] = user["id"]
    session["role"] = user["role"]

    return jsonify(
        user={"id": user["id"], "email": user["email"], "role": user["role"]}
    )


@api.post("/api/v1/auth/logout")
def logout():
    session.clear()
    return jsonify(status="logged out")


@api.get("/api/v1/me")
@login_required
def me():
    return jsonify(id=g.user["id"], email=g.user["email"], role=g.user["role"])


@api.post("/api/v1/users")
@role_required("admin")
def create_user():
    body = request.get_json(silent=True) or {}
    if (
        not body.get("email")
        or not body.get("password")
        or body.get("role") not in {"admin", "editor", "viewer"}
    ):
        return jsonify(error="email, password, and a valid role are required"), 400

    try:
        db = get_db()
        cur = db.execute(
            "INSERT INTO users(email,password_hash,role) VALUES(?,?,?)",
            (
                body["email"].lower().strip(),
                generate_password_hash(body["password"]),
                body["role"],
            ),
        )
        db.commit()
    except Exception:
        return jsonify(error="email already exists"), 409

    audit("user.created", metadata={"user_id": cur.lastrowid, "role": body["role"]})
    return jsonify(id=cur.lastrowid), 201


@api.get("/api/v1/users")
@role_required("admin")
def list_users():
    rows = (
        get_db()
        .execute("SELECT id,email,role,active,created_at FROM users ORDER BY email")
        .fetchall()
    )

    return jsonify(users=[dict(row) for row in rows])


@api.get("/api/v1/secrets")
@login_required
def list_secrets():
    rows = (
        get_db()
        .execute(
            "SELECT id,name,description,owner_id,created_at,updated_at FROM secrets ORDER BY name"
        )
        .fetchall()
    )

    return jsonify(secrets=[dict(row) for row in rows if can_access(row, "read")])


@api.post("/api/v1/secrets")
@role_required("admin", "editor")
def create_secret():
    body = request.get_json(silent=True) or {}
    if not body.get("name") or not isinstance(body.get("value"), str):
        return jsonify(error="name and string value are required"), 400
    db = get_db()
    cur = db.execute(
        "INSERT INTO secrets(name,description,ciphertext,owner_id) VALUES(?,?,?,?)",
        (body["name"], body.get("description", ""), "pending", g.user["id"]),
    )
    secret_id = cur.lastrowid

    ciphertext = encrypt(
        body["value"],
        current_app.config["SECRET_ENCRYPTION_KEY"],
        f"secret/{body['name']}",
    )
    db.execute("UPDATE secrets SET ciphertext=? WHERE id=?", (ciphertext, secret_id))
    db.commit()
    audit("secret.created", secret_id)

    return jsonify(id=secret_id, name=body["name"]), 201


def get_secret(secret_id):
    return get_db().execute("SELECT * FROM secrets WHERE id=?", (secret_id,)).fetchone()


@api.get("/api/v1/secrets/<int:secret_id>")
@login_required
def read_secret(secret_id):
    secret = get_secret(secret_id)
    if not secret or not can_access(secret, "read"):
        return jsonify(error="secret not found"), 404

    value = decrypt(
        secret["ciphertext"],
        current_app.config["SECRET_ENCRYPTION_KEY"],
        f"secret/{secret['name']}",
    )
    audit("secret.read", secret_id)

    return jsonify(
        id=secret_id,
        name=secret["name"],
        description=secret["description"],
        value=value,
    )


@api.put("/api/v1/secrets/<int:secret_id>")
@role_required("admin", "editor")
def update_secret(secret_id):
    secret = get_secret(secret_id)
    if not secret or not can_access(secret, "write"):
        return jsonify(error="secret not found"), 404

    body = request.get_json(silent=True) or {}
    if not isinstance(body.get("value"), str):
        return jsonify(error="string value is required"), 400

    db = get_db()
    cipher = encrypt(
        body["value"],
        current_app.config["SECRET_ENCRYPTION_KEY"],
        f"secret/{secret['name']}",
    )
    db.execute(
        "UPDATE secrets SET ciphertext=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",
        (cipher, secret_id),
    )
    db.commit()
    audit("secret.updated", secret_id)

    return jsonify(status="updated")


@api.post("/api/v1/secrets/<int:secret_id>/access")
@role_required("admin")
def grant_access(secret_id):
    body = request.get_json(silent=True) or {}
    if body.get("access") not in {"read", "write"} or not body.get("user_id"):
        return jsonify(error="user_id and access (read or write) are required"), 400

    if not get_secret(secret_id):
        return jsonify(error="secret not found"), 404

    db = get_db()
    db.execute(
        "INSERT OR REPLACE INTO secret_acl(secret_id,user_id,access) VALUES(?,?,?)",
        (secret_id, body["user_id"], body["access"]),
    )
    db.commit()
    audit(
        "secret.access_granted",
        secret_id,
        {"user_id": body["user_id"], "access": body["access"]},
    )

    return jsonify(status="granted")


@api.get("/api/v1/vault/export")
@login_required
def export_vault():
    rows = (
        get_db()
        .execute(
            "SELECT id,name,description,ciphertext,owner_id,created_at,updated_at FROM secrets ORDER BY id"
        )
        .fetchall()
    )

    return jsonify(
        format="vault-export-v1",
        secrets=[dict(row) for row in rows if can_access(row, "read")],
    )


@api.post("/api/v1/vault/import")
@role_required("admin")
def import_vault():
    body = request.get_json(silent=True) or {}
    if body.get("format") != "vault-export-v1" or not isinstance(
        body.get("secrets"), list
    ):
        return jsonify(error="a vault-export-v1 document is required"), 400

    if not isinstance(body.get("key"), str) or not body["key"].strip():
        return jsonify(error="the source vault key is required"), 400

    try:
        source_key = base64.urlsafe_b64decode(
            body["key"].strip() + "=" * (-len(body["key"].strip()) % 4)
        )
    except (ValueError, binascii.Error):
        return jsonify(error="the source vault key must be URL-safe base64"), 400

    if len(source_key) != 32:
        return jsonify(error="the source vault key must decode to 32 bytes"), 400

    db = get_db()
    existing_names = {row["name"] for row in db.execute("SELECT name FROM secrets")}
    seen_names = set()
    prepared = []
    try:
        for item in body["secrets"]:
            if (
                not isinstance(item, dict)
                or not isinstance(item.get("name"), str)
                or not item["name"].strip()
            ):
                raise ValueError("each imported secret needs a name")

            name = item["name"]
            if name in existing_names or name in seen_names:
                raise ValueError(f"secret name already exists: {name}")

            if not isinstance(item.get("ciphertext"), str):
                raise ValueError(f"secret {name} has invalid ciphertext")

            raw = base64.urlsafe_b64decode(
                item["ciphertext"].encode() + b"=" * (-len(item["ciphertext"]) % 4)
            )
            if len(raw) < 12 + 16:
                raise ValueError(f"secret {name} has invalid ciphertext")

            nonce, encrypted = raw[:12], raw[12:]
            value = (
                AESGCM(source_key)
                .decrypt(nonce, encrypted, f"secret/{name}".encode())
                .decode()
            )

            destination = AESGCM(current_app.config["SECRET_ENCRYPTION_KEY"]).encrypt(
                nonce, value.encode(), f"secret/{name}".encode()
            )
            prepared.append(
                (
                    name,
                    item.get("description", ""),
                    base64.urlsafe_b64encode(nonce + destination).decode(),
                    item,
                )
            )
            seen_names.add(name)
    except (
        ValueError,
        TypeError,
        UnicodeDecodeError,
        InvalidTag,
        binascii.Error,
    ) as exc:
        return jsonify(error=f"vault import rejected: {exc}"), 400

    imported_ids = []
    try:
        db.execute("BEGIN")
        used_ids = {row["id"] for row in db.execute("SELECT id FROM secrets")}
        for name, description, ciphertext, item in prepared:
            imported_id = item.get("id")
            if (
                not isinstance(imported_id, int)
                or imported_id <= 0
                or imported_id in used_ids
            ):
                imported_id = None

            if imported_id is None:
                cur = db.execute(
                    "INSERT INTO secrets(name,description,ciphertext,owner_id) VALUES(?,?,?,?)",
                    (
                        name,
                        description if isinstance(description, str) else "",
                        ciphertext,
                        g.user["id"],
                    ),
                )
                imported_id = cur.lastrowid
            else:
                db.execute(
                    "INSERT INTO secrets(id,name,description,ciphertext,owner_id) VALUES(?,?,?,?,?)",
                    (
                        imported_id,
                        name,
                        description if isinstance(description, str) else "",
                        ciphertext,
                        g.user["id"],
                    ),
                )
            used_ids.add(imported_id)
            imported_ids.append(imported_id)
        db.commit()
    except Exception:
        db.rollback()
        return jsonify(error="vault import failed; no secrets were added"), 400

    audit("vault.imported", metadata={"records": len(imported_ids)})
    return jsonify(status="imported", records=len(imported_ids), ids=imported_ids), 201


@api.get("/api/v1/audit")
@role_required("admin")
def audit_log():
    rows = (
        get_db()
        .execute("SELECT * FROM audit_log ORDER BY id DESC LIMIT 500")
        .fetchall()
    )
    return jsonify(events=[dict(row) for row in rows])
