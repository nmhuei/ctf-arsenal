from itertools import permutations, product
from datetime import datetime, timezone, timedelta

TARGET=(0x670e8462,0x306591b4,0x8372919d)

# ZipCrypto CRC table
tab=[]
for i in range(256):
    c=i
    for _ in range(8):
        c=(c>>1) ^ (0xedb88320 if c&1 else 0)
    tab.append(c & 0xffffffff)

def upd(k,b):
    k0=((k[0]>>8)^tab[(k[0]^b)&255]) & 0xffffffff
    k1=((k[1]+(k0&255))*134775813+1) & 0xffffffff
    k2=((k[2]>>8)^tab[(k[2]^(k1>>24))&255]) & 0xffffffff
    return k0,k1,k2

def keys(s):
    k=(0x12345678,0x23456789,0x34567890)
    for b in s:
        k=upd(k,b)
    return k

mid="3601188fbcc04a5da1a59be3b5383dfb"
midU=mid.upper()
miduuid=f"{mid[:8]}-{mid[8:12]}-{mid[12:16]}-{mid[16:20]}-{mid[20:]}"
short="centosstream9"
fqdn="centosstream9.linuxvmimages.local"
user="centos"
epoch="1788885121"

dt=datetime.fromtimestamp(int(epoch),timezone.utc)
dates={
    dt.strftime("%Y%m%d"), dt.strftime("%Y-%m-%d"),
    dt.strftime("%Y%m%d%H%M%S"), dt.strftime("%Y%m%d_%H%M%S"),
    dt.strftime("%Y-%m-%d_%H-%M-%S"), dt.strftime("%Y-%m-%dT%H:%M:%S"),
    dt.strftime("%Y%m%d-%H%M%S"), dt.strftime("%Y%m%d_%H%M%S_UTC"),
}
# Also common local-time variants UTC+7 in case localtime() was used elsewhere.
dt7=dt.astimezone(timezone(timedelta(hours=7)))
dates |= {
    dt7.strftime("%Y%m%d"), dt7.strftime("%Y-%m-%d"),
    dt7.strftime("%Y%m%d%H%M%S"), dt7.strftime("%Y%m%d_%H%M%S"),
    dt7.strftime("%Y-%m-%d_%H-%M-%S"), dt7.strftime("%Y-%m-%dT%H:%M:%S"),
}

ids=[mid,midU,miduuid,miduuid.upper()]
hosts=[short,fqdn,short.upper(),fqdn.upper()]
users=[user,user.upper()]
times=[epoch,*sorted(dates)]
prefixes=["audit","sys_audit","sysaudit","collector","sys_audit_collector",
          "documents_staging","documents_staging.zip","backup","archive","secure",
          "metrobank","MetroBank","CSCV2026","cscv2026"]
seps=["","_","-",":",".","@","#","|","::","/"]

seen=set(); count=0
def check(s, note=""):
    global count
    if isinstance(s,str): b=s.encode()
    else: b=s
    if b in seen: return False
    seen.add(b); count+=1
    if keys(b)==TARGET:
        print("MATCH",repr(b.decode("latin1")),note)
        open("script/offline_audit/archive_password.txt","wb").write(b)
        return True
    return False

# Atoms alone, including possible retained trailing newline from fgets.
atoms=ids+hosts+users+times+prefixes
for a in atoms:
    if check(a,"atom"): raise SystemExit
for a in ids:
    for nl in ["\n","\r\n"]:
        if check(a+nl,"machine-id newline"): raise SystemExit

# Strongest pair/triple families: hostname, machine-id, user, time.
groups=[hosts,ids,users,times]
for A,B in [(hosts,ids),(ids,hosts),(users,ids),(ids,users),(hosts,times),(times,hosts),(ids,times),(times,ids)]:
    for a,b,sep in product(A,B,seps):
        if check(a+sep+b,"pair"): raise SystemExit

core_groups=[hosts,ids,times,users]
# Permutations of three semantic groups; same delimiter or two independent delimiters.
for gi in permutations(range(4),3):
    pools=[core_groups[i] for i in gi]
    for a,b,c in product(*pools):
        for s1 in seps:
            # common same-delimiter form
            if check(a+s1+b+s1+c,"triple same sep"): raise SystemExit
        for s1,s2 in product(["_","-",":","@","."], repeat=2):
            if check(a+s1+b+s2+c,"triple mixed sep"): raise SystemExit

# Prefix + high-value core combinations.
for pref in prefixes:
    for ident in ids:
        for sep in seps:
            if check(pref+sep+ident,"prefix+mid"): raise SystemExit
            if check(ident+sep+pref,"mid+prefix"): raise SystemExit
    for h in hosts:
        for ident in ids:
            for s1,s2 in product(["","_","-",":","@","."],repeat=2):
                if check(pref+s1+h+s2+ident,"prefix+host+mid"): raise SystemExit
                if check(h+s1+ident+s2+pref,"host+mid+prefix"): raise SystemExit

# Common wrappers / labels.
base=list(seen)
for b in base:
    try: s=b.decode("ascii")
    except: continue
    if len(s)>120: continue
    for pre,suf in [("","!"),("","@"),("","2026"),("","!2026"),("","_2026"),
                    ("["," ]"),("{","}"),("CSCV{","}"),("cscv2026{","}"),
                    ("zip:",""),("pass:",""),("password:","")]:
        if check(pre+s+suf,"wrapper/suffix"): raise SystemExit

print("NO_MATCH",count)
