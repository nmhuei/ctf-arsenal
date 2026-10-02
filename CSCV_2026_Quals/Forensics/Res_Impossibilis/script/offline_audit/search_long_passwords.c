#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
static uint32_t table[256];
static size_t runs, bytes, updates, partial_matches;
static uint32_t crc(uint32_t x, unsigned char c) {return (x >> 8) ^ table[(x ^ c) & 255];}
static void check(const unsigned char *p, size_t n, size_t offset) {
    if (n <= 128) return;
    runs++; bytes += n;
    for (size_t i = 0; i + 12 <= n; i++) {
        uint32_t a = 0x12345678;
        for (size_t j = i; j < n && j < i + 128; j++) {
            a = crc(a, p[j]); updates++;
            if (j-i+1 < 12 || a != 0x670e8462U) continue;
            partial_matches++;
            uint32_t x = 0x12345678, y = 0x23456789, z = 0x34567890;
            for (size_t k = i; k <= j; k++) {
                x = crc(x, p[k]);
                y = (y + (x & 255)) * 134775813U + 1;
                z = crc(z, y >> 24);
            }
            if (y == 0x306591b4U && z == 0x8372919dU) {
                printf("VERIFIED offset=%zx length=%zu password=%.*s\n", offset+i, j-i+1, (int)(j-i+1), p+i);
                FILE *out = fopen("script/offline_audit/archive_password.txt", "wb");
                fwrite(p+i, 1, j-i+1, out); fclose(out); exit(0);
            }
        }
    }
}
int main(void) {
    for (unsigned i = 0; i < 256; i++) {
        uint32_t c = i;
        for (int j = 0; j < 8; j++) c = (c>>1) ^ ((c&1) ? 0xedb88320 : 0);
        table[i] = c;
    }
    int fd = open("script/evidence/mem.clean", O_RDONLY);
    struct stat st;
    if (fd < 0 || fstat(fd, &st)) return 2;
    const unsigned char *m = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (m == MAP_FAILED) return 2;
    size_t start = 0;
    for (size_t i = 0; i < (size_t)st.st_size; i++) {
        if (m[i] >= 32 && m[i] <= 126) continue;
        if (i > start) check(m+start, i-start, start);
        start = i+1;
    }
    check(m+start, st.st_size-start, start);
    printf("Long runs=%zu bytes=%zu CRC updates=%zu partial CRC matches=%zu; no full key match\n", runs, bytes, updates, partial_matches);
    return 0;
}
