import base64

_CRED_FRAGMENT_X = "ZmxhZ3tmMTg3NjA="
_CRED_FRAGMENT_Y = "MTM1OTYxYTVkfQ=="
_CRED_FRAGMENT_Z = "NS04MTcwLTdiYQ=="
_CRED_FRAGMENT_W = "NDMtZTc3MS00NjI="
_CRED_REASSEMBLY_ORDER = ["X", "W", "Z", "Y"]

fragments_by_label = {
    "X": _CRED_FRAGMENT_X,
    "Y": _CRED_FRAGMENT_Y,
    "Z": _CRED_FRAGMENT_Z,
    "W": _CRED_FRAGMENT_W
}

decoded = b"".join([base64.b64decode(fragments_by_label[label]) for label in _CRED_REASSEMBLY_ORDER])
flag = decoded.decode("utf-8")
print("Flag:", flag)
