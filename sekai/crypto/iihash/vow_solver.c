#define _GNU_SOURCE
#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <pthread.h>
#include <stdatomic.h>

static const uint8_t kSecret[192] = {
    0xb8, 0xfe, 0x6c, 0x39, 0x23, 0xa4, 0x4b, 0xbe, 0x7c, 0x01, 0x81, 0x2c, 0xf7, 0x21, 0xad, 0x1c,
    0xde, 0xd4, 0x6d, 0xe9, 0x83, 0x90, 0x97, 0xdb, 0x72, 0x40, 0xa4, 0xa4, 0xb7, 0xb3, 0x67, 0x1f,
    0xcb, 0x79, 0xe6, 0x4e, 0xcc, 0xc0, 0xe5, 0x78, 0x82, 0x5a, 0xd0, 0x7d, 0xcc, 0xff, 0x72, 0x21,
    0xb8, 0x08, 0x46, 0x74, 0xf7, 0x43, 0x24, 0x8e, 0xe0, 0x35, 0x90, 0xe6, 0x81, 0x3a, 0x26, 0x4c,
    0x3c, 0x28, 0x52, 0xbb, 0x91, 0xc3, 0x00, 0xcb, 0x88, 0xd0, 0x65, 0x8b, 0x1b, 0x53, 0x2e, 0xa3,
    0x71, 0x64, 0x48, 0x97, 0xa2, 0x0d, 0xf9, 0x4e, 0x38, 0x19, 0xef, 0x46, 0xa9, 0xde, 0xac, 0xd8,
    0xa8, 0xfa, 0x76, 0x3f, 0xe3, 0x9c, 0x34, 0x3f, 0xf9, 0xdc, 0xbb, 0xc7, 0xc7, 0x0b, 0x4f, 0x1d,
    0x8a, 0x51, 0xe0, 0x4b, 0xcd, 0xb4, 0x59, 0x31, 0xc8, 0x9f, 0x7e, 0xc9, 0xd9, 0x78, 0x73, 0x64,
    0xea, 0xc5, 0xac, 0x83, 0x34, 0xd3, 0xeb, 0xc3, 0xc5, 0x81, 0xa0, 0xff, 0xfa, 0x13, 0x63, 0xeb,
    0x17, 0x0d, 0xdd, 0x51, 0xb7, 0xf0, 0xda, 0x49, 0xd3, 0x16, 0x55, 0x26, 0x29, 0xd4, 0x68, 0x9e,
    0x2b, 0x16, 0xbe, 0x58, 0x7d, 0x47, 0xa1, 0xfc, 0x8f, 0xf8, 0xb8, 0xd1, 0x7a, 0xd0, 0x31, 0xce,
    0x45, 0xcb, 0x3a, 0x8f, 0x95, 0x16, 0x04, 0x28, 0xaf, 0xd7, 0xfb, 0xca, 0xbb, 0x4b, 0x40, 0x7e,
};

static uint8_t secret[192];
static uint64_t old_acc[8];

static void derive_secret_c(uint64_t seed) {
    if (seed == 0) {
        memcpy(secret, kSecret, 192);
        return;
    }
    for (int i = 0; i < 12; i++) {
        uint64_t v0 = *(uint64_t*)(kSecret + 16 * i);
        uint64_t v1 = *(uint64_t*)(kSecret + 16 * i + 8);
        *(uint64_t*)(secret + 16 * i) = v0 + seed;
        *(uint64_t*)(secret + 16 * i + 8) = v1 - seed;
    }
}

static inline uint64_t mul128_fold64(uint64_t lhs, uint64_t rhs) {
    unsigned __int128 p = (unsigned __int128)lhs * (unsigned __int128)rhs;
    return (uint64_t)p ^ (uint64_t)(p >> 64);
}

static inline uint64_t hash64(uint64_t x) {
    x ^= x >> 33;
    x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33;
    x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33;
    return x;
}

static inline uint64_t mix_word(uint64_t w, uint64_t sec) {
    uint64_t v = w ^ sec;
    return (uint64_t)((uint32_t)v) * (uint64_t)(v >> 32);
}

// Pair 0 High:
static inline uint64_t pair0_high(uint64_t w0) {
    uint64_t s0_0_l = *(uint64_t*)(secret + 11);
    uint64_t sec0 = *(uint64_t*)(secret + 121);
    uint64_t sec1 = *(uint64_t*)(secret + 129);
    uint64_t mix0 = mix_word(w0, sec0);
    uint64_t w1 = s0_0_l - old_acc[0] - mix0;
    uint64_t mix1 = mix_word(w1, sec1);
    uint64_t a0 = s0_0_l;
    uint64_t a1 = old_acc[1] + w0 + mix1;
    uint64_t s0_h = *(uint64_t*)(secret + 117);
    uint64_t s1_h = *(uint64_t*)(secret + 125);
    return mul128_fold64(a0 ^ s0_h, a1 ^ s1_h);
}

// Pair 2 High:
static inline uint64_t pair2_high(uint64_t w4) {
    uint64_t s0_2_l = *(uint64_t*)(secret + 11 + 32);
    uint64_t sec4 = *(uint64_t*)(secret + 121 + 32);
    uint64_t sec5 = *(uint64_t*)(secret + 121 + 40);
    uint64_t mix4 = mix_word(w4, sec4);
    uint64_t w5 = s0_2_l - old_acc[4] - mix4;
    uint64_t mix5 = mix_word(w5, sec5);
    uint64_t a4 = s0_2_l;
    uint64_t a5 = old_acc[5] + w4 + mix5;
    uint64_t s0_h = *(uint64_t*)(secret + 117 + 32);
    uint64_t s1_h = *(uint64_t*)(secret + 117 + 40);
    return mul128_fold64(a4 ^ s0_h, a5 ^ s1_h);
}

// Pair 1 Low:
static inline uint64_t pair1_low(uint64_t w2) {
    uint64_t s0_1_h = *(uint64_t*)(secret + 117 + 16);
    uint64_t sec2 = *(uint64_t*)(secret + 121 + 16);
    uint64_t sec3 = *(uint64_t*)(secret + 121 + 24);
    uint64_t mix2 = mix_word(w2, sec2);
    uint64_t w3 = s0_1_h - old_acc[2] - mix2;
    uint64_t mix3 = mix_word(w3, sec3);
    uint64_t a2 = s0_1_h;
    uint64_t a3 = old_acc[3] + w2 + mix3;
    uint64_t s0_l = *(uint64_t*)(secret + 11 + 16);
    uint64_t s1_l = *(uint64_t*)(secret + 11 + 24);
    return mul128_fold64(a2 ^ s0_l, a3 ^ s1_l);
}

// Pair 3 Low:
static inline uint64_t pair3_low(uint64_t w6) {
    uint64_t s0_3_h = *(uint64_t*)(secret + 117 + 48);
    uint64_t sec6 = *(uint64_t*)(secret + 121 + 48);
    uint64_t sec7 = *(uint64_t*)(secret + 121 + 56);
    uint64_t mix6 = mix_word(w6, sec6);
    uint64_t w7 = s0_3_h - old_acc[6] - mix6;
    uint64_t mix7 = mix_word(w7, sec7);
    uint64_t a6 = s0_3_h;
    uint64_t a7 = old_acc[7] + w6 + mix7;
    uint64_t s0_l = *(uint64_t*)(secret + 11 + 48);
    uint64_t s1_l = *(uint64_t*)(secret + 11 + 56);
    return mul128_fold64(a6 ^ s0_l, a7 ^ s1_l);
}

typedef uint64_t (*eval_fn)(uint64_t);

static eval_fn cur_fA;
static eval_fn cur_fB_raw;
static uint64_t cur_target;

static inline uint64_t v_step(uint64_t z) {
    uint64_t h = hash64(z);
    if (h & 1) {
        return cur_target - cur_fB_raw(h >> 1);
    } else {
        return cur_fA(h >> 1);
    }
}

#define DP_BITS 17
#define DP_MASK ((1ULL << DP_BITS) - 1)
#define MAX_STEPS (1ULL << 21)

typedef struct {
    uint64_t point;
    uint64_t start;
    uint32_t len;
} DP;

#define HASH_BITS 22
#define HASH_SIZE (1ULL << HASH_BITS)
#define HASH_MASK (HASH_SIZE - 1)

static DP* dp_table;
static pthread_mutex_t table_lock = PTHREAD_MUTEX_INITIALIZER;
static atomic_bool sol_found = 0;
static uint64_t out_x = 0;
static uint64_t out_y = 0;

static void v_insert_and_check(uint64_t point, uint64_t start, uint32_t len) {
    uint64_t idx = hash64(point) & HASH_MASK;
    pthread_mutex_lock(&table_lock);
    if (sol_found) {
        pthread_mutex_unlock(&table_lock);
        return;
    }
    for (int probe = 0; probe < 256; probe++) {
        uint64_t cur_idx = (idx + probe) & HASH_MASK;
        if (dp_table[cur_idx].point == 0) {
            dp_table[cur_idx] = (DP){point, start, len};
            pthread_mutex_unlock(&table_lock);
            return;
        }
        if (dp_table[cur_idx].point == point && dp_table[cur_idx].start != start) {
            uint64_t p1 = dp_table[cur_idx].start;
            uint64_t p2 = start;
            uint32_t l1 = dp_table[cur_idx].len;
            uint32_t l2 = len;
            while (l1 > l2) { p1 = v_step(p1); l1--; }
            while (l2 > l1) { p2 = v_step(p2); l2--; }
            uint64_t prev1 = p1, prev2 = p2;
            while (p1 != p2) {
                prev1 = p1; prev2 = p2;
                p1 = v_step(p1);
                p2 = v_step(p2);
            }
            if (prev1 != prev2) {
                uint64_t h1 = hash64(prev1);
                uint64_t h2 = hash64(prev2);
                if ((h1 & 1) != (h2 & 1)) {
                    uint64_t x = (h1 & 1) ? (h2 >> 1) : (h1 >> 1);
                    uint64_t y = (h1 & 1) ? (h1 >> 1) : (h2 >> 1);
                    if (cur_fA(x) + cur_fB_raw(y) == cur_target) {
                        out_x = x;
                        out_y = y;
                        sol_found = 1;
                    }
                }
            }
            pthread_mutex_unlock(&table_lock);
            return;
        }
    }
    pthread_mutex_unlock(&table_lock);
}

static void* v_worker(void* arg) {
    uint64_t s = (uint64_t)arg * 0x9e3779b97f4a7c15ULL + (uint64_t)time(NULL);
    while (!sol_found) {
        s = hash64(s + 1);
        uint64_t curr = s;
        uint32_t len = 0;
        while ((curr & DP_MASK) != 0 && len < MAX_STEPS) {
            curr = v_step(curr);
            len++;
        }
        if ((curr & DP_MASK) == 0 && len > 0) {
            v_insert_and_check(curr, s, len);
        }
    }
    return NULL;
}

static void solve_equation(eval_fn fa, eval_fn fb, uint64_t target, uint64_t* rx, uint64_t* ry) {
    cur_fA = fa;
    cur_fB_raw = fb;
    cur_target = target;
    sol_found = 0;
    memset(dp_table, 0, HASH_SIZE * sizeof(DP));

    pthread_t th[12];
    for (int i = 0; i < 12; i++) {
        pthread_create(&th[i], NULL, v_worker, (void*)(uint64_t)(i + 1));
    }
    for (int i = 0; i < 12; i++) {
        pthread_join(th[i], NULL);
    }
    *rx = out_x;
    *ry = out_y;
}

int main(int argc, char** argv) {
    if (argc < 4) {
        fprintf(stderr, "Usage: %s <seed> <target_sum_low> <target_sum_high>\n", argv[0]);
        return 1;
    }
    uint64_t seed = strtoull(argv[1], NULL, 0);
    uint64_t target_sum_low = strtoull(argv[2], NULL, 0);
    uint64_t target_sum_high = strtoull(argv[3], NULL, 0);

    derive_secret_c(seed);

    // Compute old_acc after 4 zero stripes
    old_acc[0] = 0xC2B2AE3DULL;
    old_acc[1] = 0x9E3779B185EBCA87ULL;
    old_acc[2] = 0xC2B2AE3D27D4EB4FULL;
    old_acc[3] = 0x165667B19E3779F9ULL;
    old_acc[4] = 0x85EBCA77C2B2AE63ULL;
    old_acc[5] = 0x85EBCA77ULL;
    old_acc[6] = 0x27D4EB2F165667C5ULL;
    old_acc[7] = 0x9E3779B1ULL;

    for (int s = 0; s < 4; s++) {
        const uint8_t* sec_s = secret + s * 8;
        for (int i = 0; i < 8; i++) {
            uint64_t sec_val = *(uint64_t*)(sec_s + 8 * i);
            uint32_t lo = (uint32_t)sec_val;
            uint32_t hi = (uint32_t)(sec_val >> 32);
            old_acc[i] += (uint64_t)lo * (uint64_t)hi;
        }
    }

    dp_table = (DP*)calloc(HASH_SIZE, sizeof(DP));

    fprintf(stderr, "[*] Solving HIGH equation (Pair 0 + Pair 2)...\n");
    uint64_t w0 = 0, w4 = 0;
    struct timespec t0, t1;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    solve_equation(pair0_high, pair2_high, target_sum_high, &w0, &w4);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    fprintf(stderr, "    HIGH solved in %.3f s: w0=0x%lx, w4=0x%lx\n",
           (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec)*1e-9, w0, w4);

    fprintf(stderr, "[*] Solving LOW equation (Pair 1 + Pair 3)...\n");
    uint64_t w2 = 0, w6 = 0;
    clock_gettime(CLOCK_MONOTONIC, &t0);
    solve_equation(pair1_low, pair3_low, target_sum_low, &w2, &w6);
    clock_gettime(CLOCK_MONOTONIC, &t1);
    fprintf(stderr, "    LOW solved in %.3f s: w2=0x%lx, w6=0x%lx\n",
           (t1.tv_sec - t0.tv_sec) + (t1.tv_nsec - t0.tv_nsec)*1e-9, w2, w6);

    uint64_t s0_0_l = *(uint64_t*)(secret + 11);
    uint64_t sec0 = *(uint64_t*)(secret + 121);
    uint64_t w1 = s0_0_l - old_acc[0] - mix_word(w0, sec0);

    uint64_t s0_1_h = *(uint64_t*)(secret + 117 + 16);
    uint64_t sec2 = *(uint64_t*)(secret + 121 + 16);
    uint64_t w3 = s0_1_h - old_acc[2] - mix_word(w2, sec2);

    uint64_t s0_2_l = *(uint64_t*)(secret + 11 + 32);
    uint64_t sec4 = *(uint64_t*)(secret + 121 + 32);
    uint64_t w5 = s0_2_l - old_acc[4] - mix_word(w4, sec4);

    uint64_t s0_3_h = *(uint64_t*)(secret + 117 + 48);
    uint64_t sec6 = *(uint64_t*)(secret + 121 + 48);
    uint64_t w7 = s0_3_h - old_acc[6] - mix_word(w6, sec6);

    printf("%lx %lx %lx %lx %lx %lx %lx %lx\n",
           w0, w1, w2, w3, w4, w5, w6, w7);
    return 0;
}
