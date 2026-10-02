#!/usr/bin/env python3
"""Descriptive RAM-key duplication sample; performs no TLS/key testing."""
import mmap, struct, json
from pathlib import Path
root=Path(__file__).resolve().parents[3]
with (root/'evidence/mem.clean').open('rb') as f:
    image=mmap.mmap(f.fileno(),0,access=mmap.ACCESS_READ)
    segments=[];offset=0;total=0
    while offset<len(image):
        magic,version,start,end,reserved=struct.unpack_from('<IIQQQ',image,offset)
        assert magic==0x4c694d45
        size=end-start+1;count=max(0,size-15)
        segments.append((offset+32,count));total+=count;offset+=32+size
    seen={};zero=0;sample_size=65536
    for i in range(sample_size):
        index=i*total//sample_size
        for data,count in segments:
            if index>=count:index-=count;continue
            key=image[data+index:data+index+16];break
        if key==bytes(16):zero+=1;continue
        seen[key]=seen.get(key,0)+1
    print(json.dumps(dict(sample_windows=sample_size,zero_windows=zero,
        nonzero_windows=sample_size-zero,unique_nonzero_keys=len(seen),
        duplicate_nonzero_instances=sample_size-zero-len(seen),
        max_nonzero_multiplicity=max(seen.values())),indent=2))
