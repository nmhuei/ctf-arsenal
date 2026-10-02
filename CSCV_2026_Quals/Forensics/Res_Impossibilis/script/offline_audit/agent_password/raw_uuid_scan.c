#define _FILE_OFFSET_BITS 64
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <omp.h>

static uint32_t crc_table[256],contribution[16][256],base_crc;
static const uint32_t before[3]={0x8e9c88b6,0xa4ea559b,0xa6fbb0aa};
static uint32_t target[3]={0x20d4d4db,0x4d3336ef,0x18c00cf1};
static const unsigned order[2][16]={
 {0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15},
 {3,2,1,0,5,4,7,6,8,9,10,11,12,13,14,15}
};
static uint32_t crc_byte(uint32_t s,unsigned char c) {
 return (s>>8)^crc_table[(s^c)&255];
}
static void format(const unsigned char bytes[16],char out[40]) {
 const char hex[]="0123456789abcdef";unsigned p=0;
 for(unsigned i=0;i<16;i++) {
  if(i==4||i==6||i==8||i==10)out[p++]='-';
  out[p++]=hex[bytes[i]>>4];out[p++]=hex[bytes[i]&15];
 }
 memcpy(out+p,"}\",",4);
}
static uint32_t crc_string(const char data[40]) {
 uint32_t s=before[0];for(unsigned j=0;j<39;j++)s=crc_byte(s,(unsigned char)data[j]);
 return s;
}
static void derive(const char *data,size_t length,uint32_t keys[3]) {
 memcpy(keys,before,sizeof(before));
 for(size_t j=0;j<length;j++) {
  keys[0]=crc_byte(keys[0],(unsigned char)data[j]);
  keys[1]=(keys[1]+(keys[0]&255))*134775813U+1;
  keys[2]=crc_byte(keys[2],keys[1]>>24);
 }
}
static void setup(void) {
 for(unsigned i=0;i<256;i++) {
  uint32_t v=i;for(unsigned j=0;j<8;j++)v=(v>>1)^((v&1)?0xedb88320:0);
  crc_table[i]=v;
 }
 unsigned char b[16]={0};char data[40];format(b,data);base_crc=crc_string(data);
 for(unsigned pos=0;pos<16;pos++) {
  for(unsigned v=0;v<256;v++) {
   b[pos]=v;format(b,data);contribution[pos][v]=crc_string(data)^base_crc;
  }
  b[pos]=0;
 }
 /* Verify the affine CRC prefilter against ordinary sequential updates. */
 uint32_t generator=1;
 for(unsigned trial=0;trial<1000;trial++) {
  uint32_t fast=base_crc;
  for(unsigned j=0;j<16;j++) {
   generator=generator*1664525U+1013904223U;b[j]=generator>>24;
   fast^=contribution[j][b[j]];
  }
  format(b,data);
  if(fast!=crc_string(data)) {fprintf(stderr,"prefilter self-test failed\n");exit(3);}
 }
}

int main(int argc,char **argv) {
 if(argc!=2 && argc!=5) {
  fprintf(stderr,"usage: %s memory-file [target0 target1 target2 hex]\n",argv[0]);return 2;
 }
 if(argc==5)for(unsigned j=0;j<3;j++)target[j]=(uint32_t)strtoul(argv[j+2],NULL,16);
 setup();
 int fd=open(argv[1],O_RDONLY);struct stat st;if(fd<0||fstat(fd,&st)||st.st_size<16)return 2;
 size_t n=st.st_size;const unsigned char *m=mmap(NULL,n,PROT_READ,MAP_PRIVATE,fd,0);
 if(m==MAP_FAILED)return 2;
 double began=omp_get_wtime();
 uint64_t network=0,nsid=0,prefilter_hits=0,matches=0;
 #pragma omp parallel for schedule(static) num_threads(4) reduction(+:network,nsid,prefilter_hits,matches)
 for(size_t offset=0;offset<=n-16;offset++) {
  const unsigned char *p=m+offset;
  if((p[8]&0xc0)!=0x80)continue;
  for(unsigned mode=0;mode<2;mode++) {
   if((p[mode?7:6]&0xf0)!=0x40)continue;
   if(mode)nsid++;else network++;
   uint32_t x=base_crc;
   for(unsigned j=0;j<16;j++)x^=contribution[j][p[order[mode][j]]];
   if(x!=target[0])continue;
   prefilter_hits++;
   unsigned char bytes[16];char data[40];uint32_t keys[3],uuid_keys[3];
   for(unsigned j=0;j<16;j++)bytes[j]=p[order[mode][j]];
   format(bytes,data);derive(data,39,keys);
   if(memcmp(keys,target,sizeof(target)))continue;
   derive(data,36,uuid_keys);matches++;
   #pragma omp critical
   {
    printf("{\"memory_offset\":\"0x%zx\",\"format\":\"%s\",\"uuid\":\"%.36s\",\"raw16_hex\":\"",offset,mode?"nsid_le":"uuid_network",data);
    for(unsigned j=0;j<16;j++)printf("%02x",p[j]);
    printf("\",\"before\":[\"%08x\",\"%08x\",\"%08x\"],\"after_uuid\":[\"%08x\",\"%08x\",\"%08x\"],\"after_suffix\":[\"%08x\",\"%08x\",\"%08x\"]}\n",
     before[0],before[1],before[2],uuid_keys[0],uuid_keys[1],uuid_keys[2],keys[0],keys[1],keys[2]);
    fflush(stdout);
   }
  }
 }
 fprintf(stderr,"{\"image_bytes\":%zu,\"offsets_checked\":%zu,\"threads\":4,\"network_candidates\":%llu,\"nsid_candidates\":%llu,\"key0_prefilter_hits\":%llu,\"full_state_matches\":%llu,\"elapsed_seconds\":%.3f}\n",
  n,n-15,(unsigned long long)network,(unsigned long long)nsid,(unsigned long long)prefilter_hits,(unsigned long long)matches,omp_get_wtime()-began);
 munmap((void*)m,n);close(fd);return 0;
}
