"""Correlate local TShark, Zeek and Suricata evidence without network access."""
from pathlib import Path
from collections import Counter
import csv
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]


def zeek_rows(filename):
    fields = []
    for line in (ROOT / 'script/zeek' / filename).read_text().splitlines():
        if line.startswith('#fields\t'):
            fields = line.split('\t')[1:]
        elif not line.startswith('#'):
            yield dict(zip(fields, line.split('\t')))


def main():
    hellos = list(csv.DictReader((HERE / 'soc_tls_clienthellos.tsv').open(), delimiter='\t'))
    randoms = {r['tls.handshake.random'] for r in hellos}
    old_randoms = set((HERE / 'tls_client_randoms.txt').read_text().split())
    key_randoms = {r.split()[1] for r in (HERE / 'tls_keys.log').read_text().splitlines() if r.strip()}
    eve = [json.loads(line) for line in (HERE / 'soc/suricata-logs/eve.json').read_text().splitlines()]
    counts = Counter(row['event_type'] for row in eve)
    stats = next(row['stats'] for row in eve if row['event_type'] == 'stats')
    ssl = {r['uid']: r for r in zeek_rows('ssl.log')}
    suri_tls = {(r['src_ip'], str(r['src_port']), r['dest_ip'], str(r['dest_port'])): r
                for r in eve if r['event_type'] == 'tls'}
    transfers = []
    for connection in zeek_rows('conn.log'):
        session = ssl.get(connection['uid'], {})
        sni = session.get('server_name', '')
        if 'userstorage.mega.co.nz' not in sni:
            continue
        flow_tuple = tuple(connection[k] for k in ('id.orig_h', 'id.orig_p', 'id.resp_h', 'id.resp_p'))
        suri = suri_tls.get(flow_tuple, {})
        streams = [r['tcp.stream'] for r in hellos if r['ip.src'] == connection['id.orig_h']
                   and r['ip.dst'] == connection['id.resp_h']
                   and r['tls.handshake.extensions_server_name'] == sni
                   and 0 <= float(r['frame.time_epoch']) - float(connection['ts']) < 2]
        transfers.append({
            'start_epoch': float(connection['ts']), 'zeek_uid': connection['uid'],
            'tuple': flow_tuple, 'sni': sni, 'tshark_stream_candidates': streams,
            'client_payload_bytes': int(connection['orig_bytes']),
            'server_payload_bytes': int(connection['resp_bytes']),
            'zeek_missed_bytes': int(connection['missed_bytes']),
            'suricata_flow_id': suri.get('flow_id'), 'community_id': suri.get('community_id'),
            'tls': suri.get('tls', {})})
    transfers.sort(key=lambda row: row['start_epoch'])
    report = {
        'tshark': {'unique_client_randoms': len(randoms), 'previous_count': len(old_randoms),
                   'tcp_clienthellos': sum(bool(r['tcp.stream']) for r in hellos),
                   'non_tcp_clienthellos': sum(not bool(r['tcp.stream']) for r in hellos),
                   'newly_observed': len(randoms - old_randoms),
                   'ram_keylog_matches': sorted(randoms & key_randoms),
                   'note': 'ClientHello rows can include QUIC; tcp.stream is blank for non-TCP traffic.'},
        'suricata': {'version': '8.0.6', 'events': dict(counts),
                     'packets': stats['decoder']['pkts'], 'packet_bytes': stats['decoder']['bytes'],
                     'invalid_packets': stats['decoder']['invalid'],
                     'tcp_reassembly_gaps': stats['tcp']['reassembly_gap'],
                     'tls_parser_errors': stats['app_layer']['error']['tls'],
                     'rules_loaded': stats['detect']['engines'][0]['rules_loaded'],
                     'note': 'Protocol analysis only; no threat signature rules loaded. Empty alerts do not establish benign traffic.'},
        'http_hosts': dict(Counter(r['http'].get('hostname') for r in eve if r['event_type'] == 'http')),
        'anomalies': dict(Counter(r['anomaly']['event'] for r in eve if r['event_type'] == 'anomaly')),
        'mega_transfers': transfers,
        'limits': ['TLS contents remain encrypted.',
                   'A client offering h2 does not establish which ALPN the TLS 1.3 server selected.',
                   'Traffic byte counts include TLS overhead and cannot identify an exact file by themselves.']
    }
    (HERE / 'soc/report.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps({k: v for k, v in report.items() if k != 'mega_transfers'}, indent=2))
    print('MEGA userstorage connections:', len(transfers))


if __name__ == '__main__':
    main()
