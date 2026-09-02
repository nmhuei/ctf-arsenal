import base64
import os

from pathlib import Path


def _key(name, default=None):
    value = os.getenv(name, default)
    if not value:
        raise RuntimeError(f"{name} must be configured")

    try:
        decoded = base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))
    except Exception as exc:
        raise RuntimeError(f"{name} must be URL-safe base64") from exc

    if len(decoded) != 32:
        raise RuntimeError(f"{name} must decode to exactly 32 bytes")

    return decoded


class Config:
    DB_PATH = Path(os.getenv("SECRET_STORAGE_DB", "/data/secrets.db"))
    SECRET_ENCRYPTION_KEY = _key("SECRET_STORAGE_KEY", "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
    BOOTSTRAP_ADMIN_EMAIL = os.getenv("BOOTSTRAP_ADMIN_EMAIL", "admin@brunnercorp.tld")
    BOOTSTRAP_ADMIN_PASSWORD = os.getenv("BOOTSTRAP_ADMIN_PASSWORD")
    COOKIE_SECURE = os.getenv("COOKIE_SECURE", "false").lower() == "true"
    SESSION_COOKIE_NAME = "secret_storage_session"
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    MAX_CONTENT_LENGTH = 64 * 1024
