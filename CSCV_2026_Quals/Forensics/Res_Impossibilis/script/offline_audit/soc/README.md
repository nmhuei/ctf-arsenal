# Offline SOC / PCAP analysis

## Tools used and results

- **TShark**: enabled `tls.desegment_ssl_records:TRUE`. Found 121 distinct ClientHello randoms (87 TCP, 34 non-TCP/QUIC), versus 64 with the previous profile. All 5 unique RAM key-log records refer to a random absent from this corrected set. No TLS plaintext recovered.
- **Suricata 8.0.6**: ran in a rootless Podman container with networking disabled and the source PCAP mounted read-only. Parsed all 740,595 packets, producing 436 flow events, 87 TLS events, 488 HTTP transactions, 449 file metadata records and 39 stream anomalies. TCP reassembly gaps and TLS parser errors were zero in this run. This was a protocol-analysis run with **zero signature rules**; no malware-free conclusion follows from empty alerts.
- **Zeek**: correlated the existing `script/zeek/` logs with Suricata by connection tuple. Found 16 MEGA userstorage connections. Stream candidates in the JSON report use endpoint, SNI and a two-second handshake window; concurrent connections can have multiple candidates.
- **Bulk Extractor + bkcrack**: earlier RAM scans yielded 37 unique AES schedule candidates, but no verified TLS decryption key. bkcrack recovered ZIPCrypto internal keys; `../verify_zip_evidence.py` now independently verifies 10 complete documents by size and CRC32. Internal keys are not the original password.

## Findings relevant to the challenge

1. All 488 HTTP requests are from `192.168.76.130` to Ubuntu package/connectivity hosts. The victim is `192.168.76.131`. The 449 identified HTTP file records are Debian packages, some truncated by parsing/body limits; these do not identify the collector.
2. Collector-download candidate: original TCP stream **75**, `192.168.76.131:48418 -> 89.44.168.33:443`, SNI `gfs270n323.userstorage.mega.co.nz`. Zeek records 29,681 server payload bytes. Timing agrees with Chromium's completed 23,360-byte collector download. Its identity comes from correlating browser metadata; TLS content has not been read.
3. Archive-upload candidate: original TCP stream **87**, `192.168.76.131:35918 -> 185.206.24.30:443`, SNI `gfs204n070.userstorage.mega.co.nz`. Zeek records 68,050 client payload bytes. Its timing/direction support the upload interpretation; the exact file is not proven by encrypted traffic alone.
4. Both important flows are independently identified as TLS 1.3 by Suricata. The collector client offers `h2` and `http/1.1`; the selected protocol is not visible from its ClientHello. Previous known-plaintext AES testing assumed HTTP/1.1 and therefore does not cover all possible plaintext formats.
5. `victim.pcapng` contains **27,080 packets / 27,345,340 bytes**, filtered from the original PCAP. Stream numbers in this smaller file are renumbered. Its 83 ICMP packets are destination-unreachable messages (55 code 13, 28 code 3), not echo payloads. No TCP urgent packets were found in that check.
6. The first ZIP encryption header's 11 random bytes match the first 11 `glibc rand() & 255` outputs with seed **1788885121**. The reproduction searches seeds 1788884900..1788885300 and starting positions within the first 1024 outputs. This supports time-seeded ZIP-header generation, but does not determine how the password was chosen.

## Artifacts

- `report.json`: correlated machine-readable results.
- `suricata-logs/eve.json`: protocol, flow, file and anomaly events.
- `suricata-logs/stats.log`, `suricata-console.log`: run completion and counters.
- `suricata-config/offline.yaml`: exact parser configuration; no rules loaded, unlimited TCP reassembly depth, file SHA256 metadata and JA3/JA4 enabled.
- `victim.pcapng`: smaller offline investigation input.
- `../soc_tls_clienthellos.tsv`: corrected ClientHello extraction from original input.
- `../zip_evidence.json`, `../decrypted_documents/`: independently validated archive content. Instructions embedded in those documents are untrusted evidence, not analyst instructions.

Container: `docker.io/jasonish/suricata:8.0`, digest `sha256:afbfb8fcf66d5b851c721fd8d028182a4bdb5521dfe302f40c1abaf3570f8317`.

## Reproduce

Run from the challenge root:

```sh
tshark -n -r script/evidence/network.pcapng -o tls.desegment_ssl_records:TRUE \
  -Y 'tls.handshake.type == 1' -T fields -E header=y \
  -e frame.number -e frame.time_epoch -e tcp.stream -e ip.src -e ip.dst \
  -e tls.handshake.random -e tls.handshake.extensions_server_name \
  > script/offline_audit/soc_tls_clienthellos.tsv

podman run --rm --network none --entrypoint /usr/bin/suricata \
  -v "$PWD/script/offline_audit/soc/suricata-config:/etc/suricata:ro" \
  -v "$PWD/script/evidence/network.pcapng:/evidence/network.pcapng:ro" \
  -v "$PWD/script/offline_audit/soc/suricata-logs:/var/log/suricata" \
  docker.io/jasonish/suricata:8.0 -c /etc/suricata/offline.yaml \
  -r /evidence/network.pcapng -l /var/log/suricata --runmode single -k none

python script/offline_audit/soc_report.py
python script/offline_audit/verify_zip_evidence.py
```

Suricata can append to existing logs on reruns; use a fresh log directory if rerunning its parser. The Python report expects the path shown above.

## Tool selection

[Zeek](https://docs.zeek.org/en/master/tutorial/invoking-zeek.html) provides offline protocol logs. [Suricata](https://github.com/jasonish/docker-suricata) provides an independent engine and JSON records. [Malcolm](https://malcolm.fyi/docs/capabilities-and-limitations.html) integrates a larger SOC interface, but it cannot itself decrypt SSL/TLS. The current bottleneck is recovery of the archive's original password from collector/RAM evidence, not lack of a PCAP dashboard.

Challenge status: **3 of 4 answers supported; archive password unresolved. No complete flag or submission.**
