#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <omp.h>
#include <openssl/sha.h>

#define N 12
#define NUM_MATRICES 4096

static uint8_t q_inv_table[256];
static uint8_t inv_matrices[NUM_MATRICES][8];
static const char D[] = "ASTERGATE/GMI/3";

static inline int bit_count8(uint8_t x) {
    return __builtin_popcount(x);
}

static inline uint8_t apply_mat(const uint8_t rows[8], uint8_t x) {
    uint8_t res = 0;
    for (int i = 0; i < 8; i++) {
        if (bit_count8(rows[i] & x) & 1) {
            res |= (1 << i);
        }
    }
    return res;
}

static uint8_t h_func(uint8_t x) {
    int b0 = (x >> 0) & 1;
    int b1 = (x >> 1) & 1;
    int b2 = (x >> 2) & 1;
    int b3 = (x >> 3) & 1;
    int o0 = b0 ^ (b2 & b3);
    int o1 = b1 ^ (b0 & b3);
    int o2 = b2 ^ (b0 & b1);
    int o3 = b3 ^ (b1 & b2);
    return o0 | (o1 << 1) | (o2 << 2) | (o3 << 3);
}

static void init_q_inv() {
    for (int x = 0; x < 256; x++) {
        uint8_t l_prime = x & 15;
        uint8_t r_prime = x >> 4;
        uint8_t r = l_prime;
        uint8_t l = r_prime ^ h_func(r);
        q_inv_table[x] = l | (r << 4);
    }
}

static int rank8(uint8_t rows[8]) {
    uint8_t a[8];
    memcpy(a, rows, 8);
    int r = 0;
    for (int c = 0; c < 8; c++) {
        int p = -1;
        for (int i = r; i < 8; i++) {
            if ((a[i] >> c) & 1) {
                p = i;
                break;
            }
        }
        if (p == -1) continue;
        uint8_t tmp = a[r];
        a[r] = a[p];
        a[p] = tmp;
        for (int i = 0; i < 8; i++) {
            if (i != r && ((a[i] >> c) & 1)) {
                a[i] ^= a[r];
            }
        }
        r++;
    }
    return r;
}

static void invert_matrix8(const uint8_t rows[8], uint8_t inv_rows[8]) {
    uint16_t a[8];
    for (int i = 0; i < 8; i++) {
        a[i] = (uint16_t)rows[i] | ((uint16_t)1 << (8 + i));
    }
    for (int c = 0; c < 8; c++) {
        int p = -1;
        for (int i = c; i < 8; i++) {
            if ((a[i] >> c) & 1) {
                p = i;
                break;
            }
        }
        uint16_t tmp = a[c];
        a[c] = a[p];
        a[p] = tmp;
        for (int i = 0; i < 8; i++) {
            if (i != c && ((a[i] >> c) & 1)) {
                a[i] ^= a[c];
            }
        }
    }
    for (int i = 0; i < 8; i++) {
        inv_rows[i] = (uint8_t)(a[i] >> 8);
    }
}

static void init_matrices() {
    #pragma omp parallel for
    for (int idx = 0; idx < NUM_MATRICES; idx++) {
        uint16_t c = 0;
        uint8_t rows[8];
        while (1) {
            uint8_t buf[64];
            int len = snprintf((char*)buf, sizeof(buf), "%s/matrix/", D);
            buf[len] = idx & 0xFF;
            buf[len+1] = (idx >> 8) & 0xFF;
            buf[len+2] = c & 0xFF;
            buf[len+3] = (c >> 8) & 0xFF;
            uint8_t hash[SHA256_DIGEST_LENGTH];
            SHA256(buf, len + 4, hash);
            memcpy(rows, hash, 8);
            if (rank8(rows) == 8) {
                break;
            }
            c++;
        }
        invert_matrix8(rows, inv_matrices[idx]);
    }
}

typedef struct {
    int offset;
    int count;
} SetInfo;

int main() {
    init_q_inv();
    printf("[*] Precomputing inverse matrices...\n");
    init_matrices();
    printf("[+] Matrices precomputed.\n");

    FILE* fp = fopen("COMPFEST_18/Cryptography/The_67th_Line/challenge/records.bin", "rb");
    if (!fp) {
        perror("records.bin");
        return 1;
    }
    fseek(fp, 0, SEEK_END);
    long sz = ftell(fp);
    fseek(fp, 0, SEEK_SET);
    uint8_t* ct_data = (uint8_t*)malloc(sz);
    fread(ct_data, 1, sz, fp);
    fclose(fp);

    SetInfo test_sets[6] = {
        {0, 512},
        {512, 512},
        {1024, 512},
        {1536, 512},
        {2048, 512},
        {2560, 512}
    };

    printf("[*] Starting key recovery for all 12 bytes...\n");
    uint32_t recovered_key[12];

    for (int b = 0; b < 12; b++) {
        uint32_t found = 0;
        int found_count = 0;

        #pragma omp parallel for reduction(+:found_count)
        for (int m_idx = 0; m_idx < 4096; m_idx++) {
            const uint8_t* inv_mat = inv_matrices[m_idx];

            uint8_t apply_lut[256];
            for (int x = 0; x < 256; x++) {
                apply_lut[x] = apply_mat(inv_mat, x);
            }

            for (int mask = 0; mask < 256; mask++) {
                int valid = 1;
                for (int s = 0; s < 6; s++) {
                    int offset = test_sets[s].offset;
                    int count = test_sets[s].count;
                    uint8_t sum = 0;
                    for (int i = 0; i < count; i++) {
                        uint8_t c_val = ct_data[(offset + i) * 12 + b];
                        uint8_t applied = apply_lut[c_val ^ mask];
                        sum ^= q_inv_table[applied];
                    }
                    if (sum != 0) {
                        valid = 0;
                        break;
                    }
                }
                if (valid) {
                    uint32_t k_val = ((uint32_t)m_idx << 8) | mask;
                    #pragma omp critical
                    {
                        found = k_val;
                    }
                    found_count++;
                }
            }
        }
        recovered_key[b] = found;
        printf("[*] Byte %2d resolved to 0x%05x (%u) [candidates: %d]\n", b, recovered_key[b], recovered_key[b], found_count);
    }

    printf("\n========================================\n");
    printf("[+] FULL RECOVERED KEY:\nkey = [");
    for (int b = 0; b < 12; b++) {
        printf("%u%s", recovered_key[b], b == 11 ? "" : ", ");
    }
    printf("]\n");

    return 0;
}
