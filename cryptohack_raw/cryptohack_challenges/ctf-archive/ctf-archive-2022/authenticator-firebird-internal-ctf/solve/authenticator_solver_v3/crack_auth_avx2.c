#define _GNU_SOURCE
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdatomic.h>
#include <immintrin.h>
#ifdef _OPENMP
#include <omp.h>
#endif

static const uint32_t IV[8] = {0x6A09E667u,0xBB67AE85u,0x3C6EF372u,0xA54FF53Au,0x510E527Fu,0x9B05688Cu,0x1F83D9ABu,0x5BE0CD19u};
static const uint8_t PERM[16]={2,6,3,10,7,0,4,13,1,11,12,5,9,14,15,8};
static inline __m256i rotr32v(__m256i x, int n){ return _mm256_or_si256(_mm256_srli_epi32(x,n), _mm256_slli_epi32(x,32-n)); }
#define Gv(a,b,c,d,x,y) do{ \
 v[a] = _mm256_add_epi32(_mm256_add_epi32(v[a], v[b]), (x)); v[d] = rotr32v(_mm256_xor_si256(v[d], v[a]), 16); v[c] = _mm256_add_epi32(v[c], v[d]); v[b] = rotr32v(_mm256_xor_si256(v[b], v[c]), 12); \
 v[a] = _mm256_add_epi32(_mm256_add_epi32(v[a], v[b]), (y)); v[d] = rotr32v(_mm256_xor_si256(v[d], v[a]), 8); v[c] = _mm256_add_epi32(v[c], v[d]); v[b] = rotr32v(_mm256_xor_si256(v[b], v[c]), 7); \
}while(0)
static inline void round_v(__m256i v[16], const __m256i m[16]){
 Gv(0,4,8,12,m[0],m[1]); Gv(1,5,9,13,m[2],m[3]); Gv(2,6,10,14,m[4],m[5]); Gv(3,7,11,15,m[6],m[7]);
 Gv(0,5,10,15,m[8],m[9]); Gv(1,6,11,12,m[10],m[11]); Gv(2,7,8,13,m[12],m[13]); Gv(3,4,9,14,m[14],m[15]);
}
static inline uint32_t check8(const uint32_t base[16], uint32_t m0, const uint32_t m1_lanes[8], const uint32_t target[8]){
 __m256i v[16], m[16];
 for(int i=0;i<8;i++) v[i]=_mm256_set1_epi32(IV[i]);
 v[8]=_mm256_set1_epi32(IV[0]); v[9]=_mm256_set1_epi32(IV[1]); v[10]=_mm256_set1_epi32(IV[2]); v[11]=_mm256_set1_epi32(IV[3]);
 v[12]=_mm256_setzero_si256(); v[13]=_mm256_setzero_si256(); v[14]=_mm256_set1_epi32(43); v[15]=_mm256_set1_epi32(11);
 for(int i=0;i<16;i++) m[i]=_mm256_set1_epi32(base[i]);
 m[0]=_mm256_set1_epi32(m0);
 m[1]=_mm256_loadu_si256((const __m256i*)m1_lanes);
 for(int r=0;r<7;r++){
   round_v(v,m);
   __m256i t0=m[PERM[0]],t1=m[PERM[1]],t2=m[PERM[2]],t3=m[PERM[3]],t4=m[PERM[4]],t5=m[PERM[5]],t6=m[PERM[6]],t7=m[PERM[7]],t8=m[PERM[8]],t9=m[PERM[9]],t10=m[PERM[10]],t11=m[PERM[11]],t12=m[PERM[12]],t13=m[PERM[13]],t14=m[PERM[14]],t15=m[PERM[15]];
   m[0]=t0;m[1]=t1;m[2]=t2;m[3]=t3;m[4]=t4;m[5]=t5;m[6]=t6;m[7]=t7;m[8]=t8;m[9]=t9;m[10]=t10;m[11]=t11;m[12]=t12;m[13]=t13;m[14]=t14;m[15]=t15;
 }
 uint32_t mask=0xffu;
 for(int i=0;i<8;i++){
   __m256i out=_mm256_xor_si256(v[i],v[i+8]);
   __m256i eq=_mm256_cmpeq_epi32(out,_mm256_set1_epi32(target[i]));
   mask &= (uint32_t)_mm256_movemask_ps(_mm256_castsi256_ps(eq));
 }
 return mask;
}
static int hexval(char c){ if(c>='0'&&c<='9') return c-'0'; if(c>='a'&&c<='f') return c-'a'+10; if(c>='A'&&c<='F') return c-'A'+10; return -1; }
static void parse_hex32(const char *hex, uint32_t out[8]){ uint8_t b[32]; for(int i=0;i<32;i++){ int hi=hexval(hex[2*i]), lo=hexval(hex[2*i+1]); if(hi<0||lo<0){fprintf(stderr,"bad hex\n"); exit(1);} b[i]=(hi<<4)|lo; } for(int i=0;i<8;i++) out[i]=(uint32_t)b[4*i]|((uint32_t)b[4*i+1]<<8)|((uint32_t)b[4*i+2]<<16)|((uint32_t)b[4*i+3]<<24); }
static void parse_hex16(const char *hex, uint8_t out[16]){ for(int i=0;i<16;i++){ int hi=hexval(hex[2*i]), lo=hexval(hex[2*i+1]); if(hi<0||lo<0){fprintf(stderr,"bad hex chal\n"); exit(1);} out[i]=(hi<<4)|lo; } }
static void make_base(const uint8_t challenge[16], const char *tag, uint32_t base[16]){ uint8_t block[64]; memset(block,0,64); memcpy(block+6,tag,21); memcpy(block+27,challenge,16); for(int i=0;i<16;i++) base[i]=(uint32_t)block[4*i]|((uint32_t)block[4*i+1]<<8)|((uint32_t)block[4*i+2]<<16)|((uint32_t)block[4*i+3]<<24); }
static void hash_digest(const char pw[6], const uint8_t challenge[16], const char *tag, uint8_t out[32]);
// scalar digest for final response
static inline uint32_t rotr32(uint32_t x, int n){ return (x>>n)|(x<<(32-n)); }
#define Gs(a,b,c,d,x,y) do{ v[a]=v[a]+v[b]+(x); v[d]=rotr32(v[d]^v[a],16); v[c]=v[c]+v[d]; v[b]=rotr32(v[b]^v[c],12); v[a]=v[a]+v[b]+(y); v[d]=rotr32(v[d]^v[a],8); v[c]=v[c]+v[d]; v[b]=rotr32(v[b]^v[c],7);}while(0)
static void round_s(uint32_t v[16], const uint32_t m[16]){ Gs(0,4,8,12,m[0],m[1]);Gs(1,5,9,13,m[2],m[3]);Gs(2,6,10,14,m[4],m[5]);Gs(3,7,11,15,m[6],m[7]);Gs(0,5,10,15,m[8],m[9]);Gs(1,6,11,12,m[10],m[11]);Gs(2,7,8,13,m[12],m[13]);Gs(3,4,9,14,m[14],m[15]); }
static void perm_s(uint32_t m[16]){ uint32_t t[16]; for(int i=0;i<16;i++) t[i]=m[PERM[i]]; for(int i=0;i<16;i++) m[i]=t[i]; }
static void hash_digest(const char pw[6], const uint8_t challenge[16], const char *tag, uint8_t out[32]){
 uint32_t base[16],m[16],v[16]; make_base(challenge,tag,base); for(int i=0;i<16;i++)m[i]=base[i];
 m[0]=(uint8_t)pw[0]|((uint32_t)(uint8_t)pw[1]<<8)|((uint32_t)(uint8_t)pw[2]<<16)|((uint32_t)(uint8_t)pw[3]<<24);
 m[1]=(uint8_t)pw[4]|((uint32_t)(uint8_t)pw[5]<<8)|((uint32_t)'H'<<16)|((uint32_t)'A'<<24);
 for(int i=0;i<8;i++) v[i]=IV[i]; v[8]=IV[0];v[9]=IV[1];v[10]=IV[2];v[11]=IV[3];v[12]=0;v[13]=0;v[14]=43;v[15]=11;
 for(int r=0;r<7;r++){ round_s(v,m); perm_s(m); }
 for(int i=0;i<8;i++){ uint32_t w=v[i]^v[i+8]; out[4*i]=w&255; out[4*i+1]=(w>>8)&255; out[4*i+2]=(w>>16)&255; out[4*i+3]=(w>>24)&255; }
}
int main(int argc,char**argv){
 if(argc<2){fprintf(stderr,"usage: %s target_hex [challenge_server_hex] [pair_start] [pair_count]\nSearch assumes challenge_client=00*16. Pair space has 3782 entries for first two password chars.\n",argv[0]); return 1;}
 const char alphabet[]="0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"; const int A=62; const int PAIRS=62*61;
 uint8_t chal0[16]={0}; uint32_t base[16],target[8]; make_base(chal0,"HANDSHAKE_FROM_SERVER",base); parse_hex32(argv[1],target);
 int pair_start = (argc>=4)? atoi(argv[3]) : 0;
 int pair_count = (argc>=5)? atoi(argv[4]) : PAIRS;
 if(pair_start<0) pair_start=0; if(pair_start>=PAIRS) pair_start%=PAIRS; if(pair_count<=0 || pair_count>PAIRS) pair_count=PAIRS;
 atomic_int found=0; char foundpw[7]={0}; unsigned long long vecs=0;
 double t0=0;
#ifdef _OPENMP
 t0=omp_get_wtime();
#endif
 #pragma omp parallel for schedule(dynamic,1) reduction(+:vecs)
 for(int off=0; off<pair_count; off++){
  int pairidx=(pair_start+off)%PAIRS;
  int i0=pairidx/61;
  int r1=pairidx%61;
  int i1=(r1<i0)?r1:r1+1;
  if(atomic_load(&found)) continue;
  for(int i2=0;i2<A;i2++) if(i2!=i0&&i2!=i1)
  for(int i3=0;i3<A;i3++) if(i3!=i0&&i3!=i1&&i3!=i2){
    if(atomic_load(&found)) continue;
    uint32_t m0=(uint8_t)alphabet[i0]|((uint32_t)(uint8_t)alphabet[i1]<<8)|((uint32_t)(uint8_t)alphabet[i2]<<16)|((uint32_t)(uint8_t)alphabet[i3]<<24);
    for(int i4=0;i4<A;i4++) if(i4!=i0&&i4!=i1&&i4!=i2&&i4!=i3){
      uint32_t lanes[8]; int idxs[8]; int cnt=0;
      for(int i5=0;i5<A;i5++) if(i5!=i0&&i5!=i1&&i5!=i2&&i5!=i3&&i5!=i4){
        lanes[cnt]=(uint8_t)alphabet[i4]|((uint32_t)(uint8_t)alphabet[i5]<<8)|((uint32_t)'H'<<16)|((uint32_t)'A'<<24); idxs[cnt]=i5; cnt++;
        if(cnt==8){ uint32_t mask=check8(base,m0,lanes,target); vecs++; if(mask && !atomic_load(&found)){ int lane=__builtin_ctz(mask); if(!atomic_exchange(&found,1)){foundpw[0]=alphabet[i0];foundpw[1]=alphabet[i1];foundpw[2]=alphabet[i2];foundpw[3]=alphabet[i3];foundpw[4]=alphabet[i4];foundpw[5]=alphabet[idxs[lane]];foundpw[6]=0;}} cnt=0; if(atomic_load(&found)) break; }
      }
      if(cnt && !atomic_load(&found)){ for(int k=cnt;k<8;k++){lanes[k]=0; idxs[k]=0;} uint32_t valid=(1u<<cnt)-1u; uint32_t mask=check8(base,m0,lanes,target)&valid; vecs++; if(mask){int lane=__builtin_ctz(mask); if(!atomic_exchange(&found,1)){foundpw[0]=alphabet[i0];foundpw[1]=alphabet[i1];foundpw[2]=alphabet[i2];foundpw[3]=alphabet[i3];foundpw[4]=alphabet[i4];foundpw[5]=alphabet[idxs[lane]];foundpw[6]=0;}} }
      if(atomic_load(&found)) break;
    }
  }
 }
 double t1=0;
#ifdef _OPENMP
 t1=omp_get_wtime();
#endif
 fprintf(stderr,"pairs=%d..%d vecs=%llu candidates~=%llu time=%.3f rate=%.1f M/s pw=%s\n",pair_start,(pair_start+pair_count-1)%PAIRS,vecs,vecs*8,t1-t0,(vecs*8)/(t1-t0)/1e6,atomic_load(&found)?foundpw:"<not found>");
 if(!atomic_load(&found)) return 2;
 printf("password=%s\n",foundpw);
 if(argc>=3 && strlen(argv[2])>=32){ uint8_t cs[16],resp[32]; parse_hex16(argv[2],cs); hash_digest(foundpw,cs,"HANDSHAKE_FROM_CLIENT",resp); printf("response_client="); for(int i=0;i<32;i++) printf("%02x",resp[i]); printf("\n"); }
 return 0;
}
