from pathlib import Path
import json,copy,re
P=Path(__file__).resolve().parent;R=P.parent/'root_files';raw=(P/'27_extensions.partial.json').read_bytes();wp=b',{"id":"wikipedia@search.mozilla.org"';prefix=raw.split(wp)[0];obj=json.loads(prefix+b']}');w=copy.deepcopy(obj['addons'][-1]);manifest=json.loads((R/'official_wikipedia/manifest.json').read_text());entries=json.loads((R/'official_wikipedia_zip_entries.json').read_text())
def h(name):
 a=0
 for c in name.encode():a=(a*37+c)%256
 return a
locales=[e['name'].split('/')[-2] for e in entries if e['name'].endswith('/messages.json')];order=sorted(locales,key=lambda code:h('chrome/browser/search-extensions/wikipedia/_locales/'+code+'/'));order=['en']+[c for c in order if c!='en'];locrows=[]
fallback=json.loads((R/'official_wikipedia/_locales/en/messages.json').read_text())
for code in order:
 messages=json.loads((R/f'official_wikipedia/_locales/{code}/messages.json').read_text());name=messages.get('extensionName',fallback['extensionName'])['message'];desc=messages.get('extensionDescription',fallback['extensionDescription'])['message'];locrows.append(dict(name=name,description=desc,creator=None,developers=None,translators=None,contributors=None,locales=[code.replace('_','-')]))
w.update(id='wikipedia@search.mozilla.org',syncGUID='{c10169c8-b166-4fbb-b166-79f58550f987}',version='1.1',defaultLocale={k:v for k,v in locrows[0].items() if k!='locales'},installDate=1788840427167,locales=locrows,rootURI='resource://search-extensions/wikipedia/')
wj=json.dumps(w,ensure_ascii=False,separators=(',',':')).encode();through=prefix+b','+wj
assert through[:len(raw)]==raw, next((i for i,(a,b) in enumerate(zip(through,raw)) if a!=b),None)
(P/'wikipedia_locale_order.json').write_text(json.dumps(order,indent=2));(P/'extensions_through_wikipedia.jsonpart').write_bytes(through)
bridge=b',{"id":"bing@search.mozilla.org","syncGUID":"{00000000-0000-0000-0000-000000000000}",';tail=(P/'27_extensions.tail.json').read_bytes();full=through+bridge+tail
print('knownprefixmatch',len(raw),'wikipediaend',len(through),'bingversionoffset',len(through+bridge),'expected',35265,'fullsize',len(full),'expected',37583)
(P/'extensions_template.json').write_bytes(full);(P/'wikipedia_rebuild_report.json').write_text(json.dumps({'known_prefix_bytes_matched':len(raw),'wikipedia_end':len(through),'bing_version_offset':len(through+bridge),'full_size':len(full),'expected_size':37583,'uuid_placeholder':'00000000-0000-0000-0000-000000000000','locales':len(order)},indent=2))
