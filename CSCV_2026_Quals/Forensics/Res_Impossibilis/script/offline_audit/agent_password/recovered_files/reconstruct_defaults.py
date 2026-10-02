#!/usr/bin/env python3
"""Reproduce four deterministic Firefox files; require directory size and CRC.

Inputs are Mozilla ESR91 default structures, not bytes carved from memory.
This script does not connect to the network. See sources.json for provenance.
"""
from pathlib import Path
import hashlib
import itertools
import json
import zlib

HERE=Path(__file__).resolve().parent
CENTRAL=HERE.parents[1]/'archive_central_records.json'
records=json.loads(CENTRAL.read_text())
report=[]

def accept(index, obj, provenance):
    data=json.dumps(obj,separators=(',',':'),ensure_ascii=False).encode()
    r=records[index]
    assert len(data)==r['plain_size']
    assert zlib.crc32(data)==int(r['crc32'],16)
    path=HERE/f'{index:02d}_{Path(r["name"]).name}'
    path.write_bytes(data)
    row=dict(index=index,name=r['name'],length=len(data),crc32=f'{zlib.crc32(data):08x}',
             sha256=hashlib.sha256(data).hexdigest(),path=str(path),
             provenance=provenance,validation='Exact ZIP central-directory length and CRC32')
    report.append(row)
    print(index,len(data),row['crc32'],path.name)

accept(32,{'experiments':{}},'Bounded reconstruction of empty Shield experiment storage')

ids=[]
for i,(icon,color,name) in enumerate([
    ('fingerprint','blue','Personal'),('briefcase','orange','Work'),
    ('dollar','green','Banking'),('cart','pink','Shopping')],1):
    ids.append(dict(userContextId=i,public=True,icon=icon,color=color,
                    l10nID=f'userContext{name}.label',
                    accessKey=f'userContext{name}.accesskey',telemetryId=i))
for i,name in [(5,'thumbnail'),(4294967295,'webextStorageLocal')]:
    ids.append(dict(userContextId=i,public=False,icon='',color='',
                    name='userContextIdInternal.'+name,accessKey=''))
accept(33,dict(version=4,lastUserContextId=5,identities=ids),
       'Mozilla ESR91 ContextualIdentityService default identities and save serialization')

mail=dict(stubEntry=True,handlers=[None,
    dict(name='Yahoo! Mail',uriTemplate='https://compose.mail.yahoo.com/?To=%s'),
    dict(name='Gmail',uriTemplate='https://mail.google.com/mail/?extsrc=mailto&url=%s')])
irc=dict(stubEntry=True,handlers=[None,
    dict(name='Mibbit',uriTemplate='https://www.mibbit.com/?url=%s')])
schemes=dict(mailto=mail,irc=irc,ircs=irc)
mime=dict(pdf='application/pdf',xml='text/xml',svg='image/svg+xml',webp='image/webp')
matches=[]
for types in itertools.permutations(mime):
    for order in itertools.permutations(schemes):
        obj=dict(defaultHandlersVersion={'en-US':4},
                 mimeTypes={mime[t]:dict(action=3,extensions=[t]) for t in types},
                 schemes={s:schemes[s] for s in order})
        data=json.dumps(obj,separators=(',',':')).encode()
        if len(data)==683 and zlib.crc32(data)==0x6df5e5fd:matches.append((types,order,obj))
assert len(matches)==1
accept(34,matches[0][2],
       'Mozilla ESR91 protocol/MIME defaults; unique matching ordering among 144 permutations')
report[-1]['mime_order']=matches[0][0]
report[-1]['scheme_order']=matches[0][1]

accept(35,dict(version=1,listeners={
    'remote-settings/monitor_changes':dict(version='"0"',sourceInfo=dict(
        moduleURI='resource://services-settings/remote-settings.js',
        symbolName='remoteSettingsBroadcastHandler'))}),
    'Mozilla ESR91 PushBroadcastService and initial RemoteSettings listener defaults')
(HERE/'reconstruction_report.json').write_text(json.dumps(report,indent=2)+'\n')
