import json

from flask.sessions import SessionMixin, SessionInterface

from .crypto import encrypt, decrypt


class EncryptedSession(dict, SessionMixin):
    pass


class EncryptedSessionInterface(SessionInterface):
    """Encrypted, authenticated cookie sessions; no session plaintext is sent to clients."""

    session_class = EncryptedSession

    def __init__(self, key: bytes):
        self.key = key

    def open_session(self, app, request):
        token = request.cookies.get(app.config["SESSION_COOKIE_NAME"])
        if not token:
            return self.session_class()
        try:
            payload = decrypt(token, self.key, "secret/session/v1")
            return self.session_class(json.loads(payload))
        except (ValueError, json.JSONDecodeError):
            return self.session_class()

    def save_session(self, app, session, response):
        name = app.config["SESSION_COOKIE_NAME"]
        if not session:
            response.delete_cookie(name)
            return

        token = encrypt(
            json.dumps(dict(session), separators=(",", ":")),
            self.key,
            "secret/session/v1",
        )

        response.set_cookie(
            name,
            token,
            httponly=True,
            secure=app.config["COOKIE_SECURE"],
            samesite=app.config["SESSION_COOKIE_SAMESITE"],
            max_age=8 * 3600,
        )
