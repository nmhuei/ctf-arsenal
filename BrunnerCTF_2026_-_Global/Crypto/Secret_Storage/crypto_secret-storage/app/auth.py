from functools import wraps

from flask import g, jsonify, session
from werkzeug.security import check_password_hash

from .db import get_db


def login_required(fn):
    @wraps(fn)
    def wrapped(*args, **kwargs):
        user_id = session.get("user_id")
        if not user_id:
            return jsonify(error="authentication required"), 401

        user = (
            get_db()
            .execute("SELECT * FROM users WHERE id=? AND active=1", (user_id,))
            .fetchone()
        )
        if not user:
            session.clear()
            return jsonify(error="authentication required"), 401

        g.user = user
        return fn(*args, **kwargs)

    return wrapped


def role_required(*roles):
    def decorator(fn):
        @wraps(fn)
        @login_required
        def wrapped(*args, **kwargs):
            if g.user["role"] not in roles:
                return jsonify(error="insufficient access level"), 403

            return fn(*args, **kwargs)

        return wrapped

    return decorator


def verify_login(email, password):
    user = (
        get_db()
        .execute(
            "SELECT * FROM users WHERE email=? AND active=1", (email.lower().strip(),)
        )
        .fetchone()
    )
    return (
        user if user and check_password_hash(user["password_hash"], password) else None
    )


def can_access(secret, mode):
    if g.user["role"] == "admin" or secret["owner_id"] == g.user["id"]:
        return True

    row = (
        get_db()
        .execute(
            "SELECT access FROM secret_acl WHERE secret_id=? AND user_id=?",
            (secret["id"], g.user["id"]),
        )
        .fetchone()
    )
    return bool(row and (row["access"] == "write" or mode == "read"))
