#!/usr/bin/env python3
from __future__ import annotations
import html,re,time
from pathlib import Path
from urllib.parse import urlencode
import requests
from bs4 import BeautifulSoup
BASE='http://50.116.30.77:5000'; USER='arif.khan@firstbangla.com'; PW='knightsquad4041337@'
OUT=Path('evidence/targetsearch'); OUT.mkdir(parents=True,exist_ok=True)
QUERIES=['RPC','Consulting','commission','400K','400000','secure','separately','account number','account ID','bank details','payment details','wire details','beneficiary','Rajesh fee','Rajesh payment','May 10','May 10 payment','SK-PRIVATE-2024-0510','transfer receipt','receipt May 10','mixing fee','external account','routing number','SWIFT','IBAN','IFSC']

def login(s):
 r=s.get(BASE+'/login',timeout=20)
 m=re.search(r'name=["\'](?:csrf_token|csrf)["\'][^>]*value=["\']([^"\']+)',r.text,re.I)
 d={'username':USER,'email':USER,'password':PW}
 if m:d['csrf_token']=html.unescape(m.group(1))
 r=s.post(BASE+'/login',data=d,timeout=20,allow_redirects=True); r.raise_for_status()
 print('LOGIN',r.url,len(r.content),'Inbox' in r.text)

def clean(x): return ' '.join(x.get_text(' ',strip=True).split())
s=requests.Session(); s.headers['User-Agent']='dfir-search-target/1.0'; login(s)
for q in QUERIES:
 try:r=s.get(BASE+'/search?'+urlencode({'q':q}),timeout=25)
 except Exception as e: print('ERR',q,e); time.sleep(3); continue
 safe=re.sub(r'[^A-Za-z0-9_.-]+','_',q)
 (OUT/(safe+'.html')).write_bytes(r.content)
 soup=BeautifulSoup(r.text,'html.parser')
 found=[]
 for a in soup.find_all('a',href=True):
  h=a['href']
  if re.fullmatch(r'/mail/(?:inbox|sent)/[^?#]+\.eml',h):
   parent=a.find_parent(['div','li','tr','article']) or a
   found.append((h,clean(parent)))
 uniq=[]; seen=set()
 for h,t in found:
  if h not in seen: seen.add(h); uniq.append((h,t))
 print('\nQUERY',repr(q),'status',r.status_code,'bytes',len(r.content),'results',len(uniq))
 for h,t in uniq[:40]: print(h,'|',t[:700])
 time.sleep(1.5)
