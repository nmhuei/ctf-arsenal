#ifndef RES_IMPOSSIBILIS_GHASH3_H
#define RES_IMPOSSIBILIS_GHASH3_H
#include <stdint.h>
#include <string.h>
#include <wmmintrin.h>
#include <tmmintrin.h>

/* Wire-order GHASH has polynomial identity 0x80,0,... . Reflect bits
 * inside each byte to obtain native little-endian polynomial coefficients.
 * All loads/stores accept unaligned addresses. No allocation or global state.
 */
static inline __m128i ghash3_reflect_bytes(__m128i x) {
    const __m128i nibble_reverse = _mm_setr_epi8(
        0,8,4,12,2,10,6,14,1,9,5,13,3,11,7,15);
    const __m128i nibble_mask = _mm_set1_epi8(15);
    __m128i lo = _mm_and_si128(x, nibble_mask);
    __m128i hi = _mm_and_si128(_mm_srli_epi16(x,4), nibble_mask);
    return _mm_or_si128(_mm_slli_epi16(_mm_shuffle_epi8(nibble_reverse,lo),4),
                       _mm_shuffle_epi8(nibble_reverse,hi));
}

/* Multiply reflected polynomial coefficients modulo
 * x^128 + x^7 + x^2 + x + 1. Three CLMULs form the 256-bit product;
 * three further CLMULs reduce it, with the final overflow <= seven bits.
 */
static inline __m128i ghash3_mul_reflected(__m128i a, __m128i b) {
    __m128i p00 = _mm_clmulepi64_si128(a,b,0x00);
    __m128i p11 = _mm_clmulepi64_si128(a,b,0x11);
    __m128i ax = _mm_xor_si128(a,_mm_srli_si128(a,8));
    __m128i bx = _mm_xor_si128(b,_mm_srli_si128(b,8));
    __m128i mid = _mm_xor_si128(_mm_clmulepi64_si128(ax,bx,0x00),
                               _mm_xor_si128(p00,p11));
    __m128i lo = _mm_xor_si128(p00,_mm_slli_si128(mid,8));
    __m128i hi = _mm_xor_si128(p11,_mm_srli_si128(mid,8));
    const __m128i modulus = _mm_set_epi64x(0,0x87);
    __m128i r0 = _mm_clmulepi64_si128(hi,modulus,0x00);
    __m128i r1 = _mm_clmulepi64_si128(hi,modulus,0x01);
    __m128i overflow = _mm_srli_si128(r1,8);
    __m128i r2 = _mm_clmulepi64_si128(overflow,modulus,0x00);
    return _mm_xor_si128(lo,_mm_xor_si128(r0,
             _mm_xor_si128(_mm_slli_si128(r1,8),r2)));
}

/* Exactly three already padded blocks, including the GCM length block.
 * h and output use conventional wire byte order.
 */
static inline void ghash3(const unsigned char h[16],
                          const unsigned char blocks[48],
                          unsigned char out[16]) {
    __m128i hr = ghash3_reflect_bytes(_mm_loadu_si128((const __m128i *)h));
    __m128i state = _mm_setzero_si128();
    for (int i=0;i<3;i++) {
        __m128i block = ghash3_reflect_bytes(
            _mm_loadu_si128((const __m128i *)(blocks+16*i)));
        state = ghash3_mul_reflected(_mm_xor_si128(state,block),hr);
    }
    _mm_storeu_si128((__m128i *)out,ghash3_reflect_bytes(state));
}

/* Optional fast path: caller can pre-reflect the constant three blocks
 * once, outside the candidate-key loop. Only H changes per candidate.
 */
static inline __m128i ghash3_pre_reflected(__m128i h_wire,
                                          const __m128i blocks_reflected[3]) {
    __m128i h = ghash3_reflect_bytes(h_wire);
    __m128i state = _mm_setzero_si128();
    for (int i=0;i<3;i++)
        state = ghash3_mul_reflected(_mm_xor_si128(state,blocks_reflected[i]),h);
    return ghash3_reflect_bytes(state);
}
#endif
