#!/usr/bin/env python3
from __future__ import annotations
import html, re, sys, time
from pathlib import Path
from urllib.parse import urljoin
import requests

BASE='http://50.116.30.77:5000'
USER='arif.khan@firstbangla.com'
PW='knightsquad4041337@'
OUT=Path('evidence/targetmail'); OUT.mkdir(parents=True,exist_ok=True)
TARGETS=[
'/mail/inbox/20231103-215000_0699_private-matter-please-keep-this-between-.eml',
'/mail/inbox/20240104-225500_0880_re-quick-question.eml',
'/mail/inbox/20240122-233000_0923_re-timing.eml',
'/mail/inbox/20240213-224700_0983_re-wallet.eml',
'/mail/inbox/20240309-231100_1041_re-the-director-again.eml',
'/mail/sent/20240321-215800_1073_logistics-update.eml',
'/mail/inbox/20240403-222000_1093_re-logistics-update.eml',
'/mail/inbox/20240424-211200_1152_re-travel-booked.eml',
]

def login(s):
 r=s.get(BASE+'/login',timeout=20)
 m=re.search(r'name=["\'](?:csrf_token|csrf)["\'][^>]*value=["\']([^"\']+)',r.text,re.I)
 data={'username':USER,'email':USER,'password':PW}
 if m:data['csrf_token']=html.unescape(m.group(1))
 r=s.post(BASE+'/login',data=data,timeout=20,allow_redirects=True)
 print('login',r.status_code,r.url,len(r.content),'Inbox' in r.text,'Sign out' in r.text)
 r.raise_for_status()

def textify(t):
 t=re.sub(r'(?is)<(script|style).*?</\1>',' ',t)
 t=re.sub(r'(?s)<[^>]+>','\n',t)
 return '\n'.join(x for x in (re.sub(r'\s+',' ',html.unescape(x)).strip() for x in t.splitlines()) if x)

s=requests.Session(); s.headers['User-Agent']='dfir-target-fetch/1.0'; login(s)
for path in TARGETS:
 for suffix in ['', '/source']:
  u=BASE+path+suffix
  try:r=s.get(u,timeout=25,allow_redirects=True)
  except Exception as e: print('ERR',u,e); continue
  safe=re.sub(r'[^A-Za-z0-9_.-]+','_',path.strip('/'))+('_source' if suffix else '')
  (OUT/(safe+'.html')).write_bytes(r.content)
  print('\n###',path+suffix,'status',r.status_code,'url',r.url,'bytes',len(r.content))
  print(textify(r.text)[:8000])
  print('LINKS')
  for m in re.finditer(r'href=["\']([^"\']+)["\']',r.text,re.I):
   h=html.unescape(m.group(1))
   if any(k in h.lower() for k in ['attach','download','source','mail/']): print(h)
  time.sleep(.8)
