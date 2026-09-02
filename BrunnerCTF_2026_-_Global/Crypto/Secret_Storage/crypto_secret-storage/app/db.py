import sqlite3

from flask import current_app, g
from werkzeug.security import generate_password_hash

from .crypto import encrypt


SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
  id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('admin','editor','viewer')),
  active INTEGER NOT NULL DEFAULT 1, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS secrets (
  id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
  ciphertext TEXT NOT NULL, associated_data TEXT NOT NULL DEFAULT '', owner_id INTEGER NOT NULL, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY(owner_id) REFERENCES users(id)
);
CREATE TABLE IF NOT EXISTS secret_acl (
  secret_id INTEGER NOT NULL, user_id INTEGER NOT NULL, access TEXT NOT NULL CHECK(access IN ('read','write')),
  PRIMARY KEY(secret_id, user_id), FOREIGN KEY(secret_id) REFERENCES secrets(id) ON DELETE CASCADE,
  FOREIGN KEY(user_id) REFERENCES users(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS audit_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT, actor_id INTEGER, action TEXT NOT NULL,
  secret_id INTEGER, metadata TEXT NOT NULL DEFAULT '{}', ip TEXT, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
"""


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(current_app.config["DB_PATH"])
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys=ON")
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db:
        db.close()


def init_db():
    db_path = current_app.config["DB_PATH"]
    db_path.parent.mkdir(parents=True, exist_ok=True)
    db = get_db()
    db.executescript(SCHEMA)
    db.commit()
    if current_app.config.get("BOOTSTRAP_ADMIN_PASSWORD"):
        email = current_app.config["BOOTSTRAP_ADMIN_EMAIL"].lower()
        db.execute(
            "INSERT OR IGNORE INTO users(email,password_hash,role) VALUES(?,?,?)",
            (
                email,
                generate_password_hash(current_app.config["BOOTSTRAP_ADMIN_PASSWORD"]),
                "admin",
            ),
        )
        db.commit()
    seed_data()


def seed_data():
    """Add safe, fictional demo records without changing an existing vault."""
    db = get_db()

    users = [
        ("maya.chen@brunnercorp.tld", "Odense2026!", "editor"),
        ("jonas.nielsen@brunnercorp.tld", "REDACTED", "viewer"),
        ("priya.shah@brunnercorp.tld", "REDACTED", "viewer"),
    ]

    for email, password, role in users:
        db.execute(
            "INSERT OR IGNORE INTO users(email,password_hash,role) VALUES(?,?,?)",
            (email, generate_password_hash(password), role),
        )
    db.commit()

    users = {
        row["email"]: row["id"]
        for row in db.execute(
            "SELECT id,email FROM users WHERE email IN (?,?,?)",
            tuple(user[0] for user in users),
        ).fetchall()
    }

    demo_secrets = [
        (
            "production-database-url",
            "Primary application database connection string",
            "postgresql://vaultops_app:demo-only@db.internal.example:5432/vaultops",
            "maya.chen@brunnercorp.tld",
        ),
        (
            "stripe-test-api-key",
            "Test-mode billing integration key",
            "sk_test_51DemoVaultOps000000000000000000",
            "maya.chen@brunnercorp.tld",
        ),
        (
            "github-deploy-token",
            "Read-only deployment token for the platform repository",
            "ghp_demoVaultOpsToken000000000000000000",
            "jonas.nielsen@brunnercorp.tld",
        ),
        (
            "s3-backup-access-key",
            "Nightly encrypted backup storage credential",
            "AKIADEMOVAULTOPS000000",
            "priya.shah@brunnercorp.tld",
        ),
    ]

    for name, description, value, owner_email in demo_secrets:
        if db.execute("SELECT 1 FROM secrets WHERE name=?", (name,)).fetchone():
            continue
        cur = db.execute(
            "INSERT INTO secrets(name,description,ciphertext,owner_id) VALUES(?,?,?,?)",
            (name, description, "pending", users[owner_email]),
        )
        ciphertext = encrypt(
            value, current_app.config["SECRET_ENCRYPTION_KEY"], f"secret/{name}"
        )
        db.execute(
            "UPDATE secrets SET ciphertext=? WHERE id=?", (ciphertext, cur.lastrowid)
        )

    acl = [
        ("github-deploy-token", "maya.chen@brunnercorp.tld", "read"),
        ("stripe-test-api-key", "jonas.nielsen@brunnercorp.tld", "read"),
        ("production-database-url", "priya.shah@brunnercorp.tld", "read"),
    ]
    for secret_name, email, access in acl:
        secret = db.execute(
            "SELECT id FROM secrets WHERE name=?", (secret_name,)
        ).fetchone()
        db.execute(
            "INSERT OR IGNORE INTO secret_acl(secret_id,user_id,access) VALUES(?,?,?)",
            (secret["id"], users[email], access),
        )

    db.commit()
