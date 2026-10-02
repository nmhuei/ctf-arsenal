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
#include "../../agent_archive/tls87/ghash3.h"
#include "native_inputs.h"

typedef struct {__m128i k[11];} aes128;
static inline __m128i extend(__m128i x,__m128i assist) {
 assist=_mm_shuffle_epi32(assist,0xff);
 x=_mm_xor_si128(x,_mm_slli_si128(x,4));
 x=_mm_xor_si128(x,_mm_slli_si128(x,4));
 x=_mm_xor_si128(x,_mm_slli_si128(x,4));
 return _mm_xor_si128(x,assist);
}
static inline void expand(const unsigned char p[16],aes128 *s) {
 s->k[0]=_mm_loadu_si128((const __m128i*)p);
 #define ROUND(i,r) s->k[i]=extend(s->k[i-1],_mm_aeskeygenassist_si128(s->k[i-1],r))
 ROUND(1,1);ROUND(2,2);ROUND(3,4);ROUND(4,8);ROUND(5,16);
 ROUND(6,32);ROUND(7,64);ROUND(8,128);ROUND(9,27);ROUND(10,54);
 #undef ROUND
}
static inline __m128i encrypt(__m128i x,const aes128 *s) {
 x=_mm_xor_si128(x,s->k[0]);
 for(unsigned i=1;i<10;i++)x=_mm_aesenc_si128(x,s->k[i]);
 return _mm_aesenclast_si128(x,s->k[10]);
}
static inline __m128i decrypt(__m128i x,const aes128 *s) {
 x=_mm_xor_si128(x,s->k[10]);
 for(unsigned i=9;i>0;i--)x=_mm_aesdec_si128(x,_mm_aesimc_si128(s->k[i]));
 return _mm_aesdeclast_si128(x,s->k[0]);
}
static inline __m128i candidate_j0(const unsigned char p[16],const __m128i blocks[3],__m128i tag) {
 aes128 s;expand(p,&s);
 __m128i h=encrypt(_mm_setzero_si128(),&s);
 __m128i g=ghash3_pre_reflected(h,blocks);
 return decrypt(_mm_xor_si128(tag,g),&s);
}
typedef struct {size_t file;uint64_t physical;size_t count;} segment;
typedef struct {size_t file;uint64_t physical;size_t count;} job;
static uint64_t le64(const unsigned char *p){uint64_t v;memcpy(&v,p,8);return v;}
static uint32_t le32(const unsigned char *p){uint32_t v;memcpy(&v,p,4);return v;}

int main(int argc,char **argv) {
 if(argc!=3 || (strcmp(argv[2],"--benchmark") && strcmp(argv[2],"--full") && strcmp(argv[2],"--all-bytes")))return 2;
 __m128i fixture[3],blocks[3];
 for(unsigned i=0;i<3;i++) {
  fixture[i]=ghash3_reflect_bytes(_mm_loadu_si128((const __m128i*)(fixture_blocks+16*i)));
  blocks[i]=ghash3_reflect_bytes(_mm_loadu_si128((const __m128i*)(target_blocks+16*i)));
 }
 unsigned char control[16];
 _mm_storeu_si128((__m128i*)control,candidate_j0(fixture_key,fixture,_mm_loadu_si128((const __m128i*)fixture_tag)));
 if(memcmp(control,fixture_j0,16)){fprintf(stderr,"native fixture FAILED\n");return 3;}
 unsigned char wrong[16]={0};
 _mm_storeu_si128((__m128i*)control,candidate_j0(wrong,fixture,_mm_loadu_si128((const __m128i*)fixture_tag)));
 if(!memcmp(control+12,"\0\0\0\1",4)){fprintf(stderr,"wrong-key fixture FAILED\n");return 3;}
 fprintf(stderr,"native fixture passed; wrong-key control rejected\n");
 __m128i tag=_mm_loadu_si128((const __m128i*)target_tag);
 _mm_storeu_si128((__m128i*)control,candidate_j0(wrong,blocks,tag));
 if(!memcmp(control+12,"\0\0\0\1",4)){fprintf(stderr,"zero key is a candidate; stopping for separate validation\n");return 4;}

 int fd=open(argv[1],O_RDONLY);struct stat st;if(fd<0||fstat(fd,&st))return 2;
 size_t n=st.st_size;const unsigned char *m=mmap(NULL,n,PROT_READ,MAP_PRIVATE,fd,0);
 if(m==MAP_FAILED)return 2;
 int all_bytes=!strcmp(argv[2],"--all-bytes");
 size_t stride=all_bytes?1:16;
 segment segments[1024];size_t ns=0,pos=0,total=0;
 while(pos<n) {
  if(pos+32>n || le32(m+pos)!=0x4c694d45 || ns>=1024)return 5;
  uint64_t start=le64(m+pos+8),end=le64(m+pos+16);
  if(end<start || end-start+1>n-pos-32)return 5;
  size_t length=end-start+1,align=all_bytes?0:((16-(start&15))&15);
  if(length>=align+16) {
   segments[ns++]=(segment){pos+32+align,start+align,((length-align-16)/stride+1)};
   total+=((length-align-16)/stride+1);
  }
  pos+=32+length;
 }
 int benchmark=!strcmp(argv[2],"--benchmark");
 job jobs[65536];size_t nj=0;
 if(benchmark) {
  for(size_t sample=0;sample<32;sample++) {
   size_t index=sample*total/32;
   for(size_t s=0;s<ns;s++) {
    if(index>=segments[s].count){index-=segments[s].count;continue;}
    size_t count=segments[s].count-index;if(count>32768)count=32768;
    jobs[nj++]=(job){segments[s].file+stride*index,segments[s].physical+stride*index,count};break;
   }
  }
 } else {
  for(size_t s=0;s<ns;s++)for(size_t at=0;at<segments[s].count;at+=262144) {
   if(nj>=65536)return 5;
   size_t count=segments[s].count-at;if(count>262144)count=262144;
   jobs[nj++]=(job){segments[s].file+stride*at,segments[s].physical+stride*at,count};
  }
 }
 for(size_t s=0;s<ns;s++)fprintf(stderr,"segment physical=0x%llx file=0x%zx file_mod16=%zu keys=%zu\n",
  (unsigned long long)segments[s].physical,segments[s].file,segments[s].file%16,segments[s].count);
 uint64_t visited=0,tested=0,zeros=0,hits=0;double began=omp_get_wtime();
 #pragma omp parallel for schedule(dynamic,1) num_threads(4) reduction(+:visited,tested,zeros,hits)
 for(size_t j=0;j<nj;j++) {
  job work=jobs[j];
  for(size_t i=0;i<work.count;i++) {
   const unsigned char *p=m+work.file+stride*i;visited++;
   uint64_t v0,v1;memcpy(&v0,p,8);memcpy(&v1,p+8,8);
   if(!(v0|v1)){zeros++;continue;}
   tested++;
   __m128i v=candidate_j0(p,blocks,tag);
   if((uint32_t)_mm_cvtsi128_si32(_mm_srli_si128(v,12))!=0x01000000U)continue;
   unsigned char j0[16];_mm_storeu_si128((__m128i*)j0,v);hits++;
   #pragma omp critical
   {
    printf("{\"file_offset\":\"0x%zx\",\"physical_offset\":\"0x%llx\",\"key\":\"",work.file+stride*i,(unsigned long long)(work.physical+stride*i));
    for(unsigned k=0;k<16;k++)printf("%02x",p[k]);
    printf("\",\"j0\":\"");for(unsigned k=0;k<16;k++)printf("%02x",j0[k]);
    printf("\"}\n");fflush(stdout);
   }
  }
 }
 double elapsed=omp_get_wtime()-began;
 fprintf(stderr,"{\"benchmark\":%s,\"threads\":4,\"candidate_positions_total\":%zu,\"visited\":%llu,\"nonzero_tested\":%llu,\"zero_instances_skipped_after_one_key_test\":%llu,\"hits\":%llu,\"elapsed_seconds\":%.6f,\"tested_keys_per_second\":%.3f,\"conservative_full_seconds\":%.3f}\n",
  benchmark?"true":"false",total,(unsigned long long)visited,(unsigned long long)tested,(unsigned long long)zeros,(unsigned long long)hits,elapsed,tested/elapsed,total*elapsed/tested);
 munmap((void*)m,n);close(fd);return 0;
}
