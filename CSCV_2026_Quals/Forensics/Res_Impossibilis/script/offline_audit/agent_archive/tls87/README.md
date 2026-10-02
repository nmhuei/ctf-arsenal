# Passive TLS stream 87 extraction

Input: the original `script/evidence/network.pcapng`, not the victim-only subset whose stream numbers differ.

Connection: `192.168.76.131:35918` to `185.206.24.30:443`. The first packet timestamp and all per-packet provenance are recorded in `metadata.json`.

`packets.tsv` was extracted by TShark using `tcp.stream == 87`. `reassemble.py` reconstructs each direction from raw TCP sequence numbers anchored at its SYN, checks every overlapping byte, and parses complete TLS records. Results:

- 130 captured packets.
- Client: 68,050 reassembled payload bytes; server: 6,288.
- Zero missing bytes, zero duplicate payload bytes, zero conflicting overlapping bytes.
- Every byte belongs to a complete TLS record; ten records in each direction.
- `client.bin` / `server.bin` contain complete directional TCP payloads.
- `client_records.json` / `server_records.json` provide each TLS record's index, header offset, payload offset, content type, legacy version, payload length and end offset.

## Captured negotiation

ServerHello selects TLS 1.3 (`supported_versions = 0304`), `TLS_AES_128_GCM_SHA256` (`0x1301`), with X25519 key exchange (`0x001d`). The ClientHello SNI is `gfs204n070.userstorage.mega.co.nz`; its sole offered ALPN is `http/1.1`. The server's ALPN selection is inside encrypted TLS 1.3 EncryptedExtensions and has not been read.

Client random: `42799c928b22c8a61bd29cf88cf7a0c2f4f892b6133e7d7b31a1a81dc86c0035`.

Server random: `17fec9b887efe9625c58fa0878cff39be81a7d81f1f41b76a5b61ea1b544dfd5`.

## Framing inference, not decrypted evidence

After the likely encrypted client Finished record, encrypted client record payload lengths are 606, 43, 16401, 16401, 16401, 16281, 23. Assuming no TLS inner padding, corresponding application lengths are 589, 26, 16384, 16384, 16384, 16264, 6.

The bulk application lengths total 65,416 bytes, exactly the archive's 65,408 bytes plus eight. This fits a masked WebSocket binary frame with a 16-bit payload length (`82 fe ff 80`, four mask bytes, then 65,408 masked bytes). The other lengths also fit a 26-byte masked control/request frame and a six-byte empty masked close frame. This is a hypothesis to guide key verification; no WebSocket header, masking key, HTTP request or decrypted TLS application data has yet been verified here.

No external service was contacted. Captured session keys and plaintext are being assessed separately by the password agent, accepting decrypted records only after authentication checks.
