#include "ghash3.h"
void test_ghash3(const unsigned char *h,const unsigned char *blocks,unsigned char *out) {
    ghash3(h,blocks,out);
}
void test_ghash3_pre(const unsigned char *h,const unsigned char *blocks,unsigned char *out) {
    __m128i bs[3];
    for(int i=0;i<3;i++)bs[i]=ghash3_reflect_bytes(_mm_loadu_si128((const __m128i *)(blocks+16*i)));
    _mm_storeu_si128((__m128i *)out,ghash3_pre_reflected(_mm_loadu_si128((const __m128i*)h),bs));
}
