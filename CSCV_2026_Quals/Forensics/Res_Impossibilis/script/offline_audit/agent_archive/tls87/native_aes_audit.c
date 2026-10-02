#define main audited_scanner_main
#include "../../agent_password/tls87/raw_aes_scan.c"
#undef main
void audit_aes(const unsigned char *key, const unsigned char *p, unsigned char *enc, unsigned char *dec) {
 aes128 s; expand(key,&s); __m128i v=_mm_loadu_si128((const __m128i*)p);
 _mm_storeu_si128((__m128i*)enc,encrypt(v,&s));
 _mm_storeu_si128((__m128i*)dec,decrypt(v,&s));
}
void audit_j0(const unsigned char *key, const unsigned char *b, const unsigned char *tag, unsigned char *out) {
 __m128i blocks[3];for(int i=0;i<3;i++)blocks[i]=ghash3_reflect_bytes(_mm_loadu_si128((const __m128i*)(b+16*i)));
 _mm_storeu_si128((__m128i*)out,candidate_j0(key,blocks,_mm_loadu_si128((const __m128i*)tag)));
}
