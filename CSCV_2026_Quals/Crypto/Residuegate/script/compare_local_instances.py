#!/usr/bin/env python3
"""Compare the supplied local container and direct binary on loopback only.

The probe records public response shapes and hashes. It does not contact a
remote host, submit a candidate, inspect process memory, or read a flag.
"""
import argparse
import hashlib
import json
import urllib.error
import urllib.request


ROUTES = {
    "objective": "/feature_a9e63777c9a2409902b702d5238a61b8",
    "json_evaluate": "/feature_11edaf0d1c4e447615614810348a3030",
    "multipart_evaluate": "/feature_c26f994e7f7d755a4602972a35430050",
    "slot": "/feature_c426f4d0ed166214ae89992cbd592932",
    "session": "/feature_fa8688cbfa3fc935ae60de224a972126",
}


def request(port, method, path, body=None, content_type=None):
    headers = {}
    if content_type:
        headers["content-type"] = content_type
    req = urllib.request.Request(
        f"http://127.0.0.1:{port}{path}",
        data=body,
        headers=headers,
        method=method,
    )
    try:
        with urllib.request.urlopen(req, timeout=3) as response:
            status, response_headers, payload = response.status, response.headers, response.read()
    except urllib.error.HTTPError as error:
        status, response_headers, payload = error.code, error.headers, error.read()
    return {
        "status": status,
        "content_type": response_headers.get("content-type", ""),
        "length": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
        "payload": payload,
    }


def public_shape(result):
    return {k: v for k, v in result.items() if k != "payload"}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ports", nargs=2, type=int, default=[5001, 5002])
    args = parser.parse_args()
    ports = args.ports

    out = {"scope": "loopback-only", "ports": ports, "routes": {}, "comparison": {}}
    for name in ("objective", "json_evaluate", "multipart_evaluate", "slot"):
        path = ROUTES[name]
        cases = {}
        for method in ("GET", "POST", "OPTIONS"):
            values = []
            for port in ports:
                if method == "POST":
                    body, content_type = b"", "application/json"
                else:
                    body, content_type = None, None
                values.append(public_shape(request(port, method, path, body, content_type)))
            cases[method] = values
        out["routes"][name] = cases

    sessions = []
    for port in ports:
        result = request( port, "POST", ROUTES["session"], b"{}", "application/json")
        session = json.loads(result["payload"])
        sessions.append({
            "response": public_shape(result),
            "session_id_length": len(session.get("session_id", "")),
            "top_keys": sorted(session),
            "static_fields": {
                "base_image_slots": session.get("base_image_slots"),
                "combination_constants": {k: session.get("combination", {}).get(k)
                                           for k in ("candidate_space", "schema", "target_slots", "variants_per_slot")},
                "limits": session.get("limits"),
                "mixing_matrix": session.get("mixing_matrix"),
                "model": session.get("model"),
                "crypto_constants": {k: session.get("crypto", {}).get(k)
                                      for k in ("n", "p1", "p2", "q")},
                "public_key_lengths": {k: len(session.get("crypto", {}).get("public_key", {}).get(k, []))
                                        for k in ("b", "neg_a")},
            },
        })
        slot_path = ROUTES["slot"] + f"?session_id={session['session_id']}&slot=0"
        slot = request(port, "GET", slot_path)
        sessions[-1]["slot0"] = public_shape(slot)
    out["sessions"] = sessions
    out["comparison"]["objective_same_sha256"] = (
        out["routes"]["objective"]["GET"][0]["sha256"] ==
        out["routes"]["objective"]["GET"][1]["sha256"]
    )
    out["comparison"]["route_matrix_same"] = all(
        values[0] == values[1]
        for cases in out["routes"].values()
        for values in cases.values()
    )
    out["comparison"]["session_static_fields_same"] = (
        sessions[0]["static_fields"] == sessions[1]["static_fields"]
    )
    out["comparison"]["session_ids_are_dynamic"] = (
        sessions[0]["session_id_length"] == sessions[1]["session_id_length"] == 32
    )
    out["comparison"]["slot0_same_sha256"] = (
        sessions[0]["slot0"]["sha256"] == sessions[1]["slot0"]["sha256"]
    )
    print(json.dumps(out, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
