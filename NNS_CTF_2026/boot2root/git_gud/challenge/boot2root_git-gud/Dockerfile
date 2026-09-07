FROM codeberg.org/forgejo/forgejo:15.0.7@sha256:1f9c1a9880425614267832ce437f8ae5f5b69e1f3219f38fc468fc37e48c1919

ENV USER="git" \
    GITEA_CUSTOM="/data/gitea" \
    FORGEJO__security__INSTALL_LOCK="true" \
    FORGEJO__database__DB_TYPE="sqlite3" \
    FORGEJO__database__PATH="/data/gitea/forgejo.db" \
    FORGEJO__server__PROTOCOL="http" \
    FORGEJO__server__HTTP_PORT="3000" \
    FORGEJO__server__DISABLE_SSH="true" \
    FORGEJO__server__OFFLINE_MODE="true" \
    FORGEJO__service__DISABLE_REGISTRATION="false" \
    FORGEJO__service__REQUIRE_SIGNIN_VIEW="false" \
    FORGEJO__service__ENABLE_CAPTCHA="false" \
    FORGEJO__service__DEFAULT_KEEP_EMAIL_PRIVATE="true" \
    FORGEJO__service__REGISTER_EMAIL_CONFIRM="false" \
    FORGEJO__mailer__ENABLED="false" \
    FORGEJO__cron__ENABLED="false" \
    FORGEJO__log__LEVEL="Warn"

EXPOSE 3000
