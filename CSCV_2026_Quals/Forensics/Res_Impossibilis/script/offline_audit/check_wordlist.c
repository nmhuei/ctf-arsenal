#include <stdio.h>
#include <stdint.h>
#include <string.h>

static uint32_t table[256];

static uint32_t crc32_byte(uint32_t value, unsigned char byte) {
    return (value >> 8) ^ table[(value ^ byte) & 0xff];
}

static int matches(const unsigned char *password, size_t length) {
    uint32_t key0 = 0x12345678, key1 = 0x23456789, key2 = 0x34567890;
    for (size_t i = 0; i < length; i++) {
        key0 = crc32_byte(key0, password[i]);
        key1 = (key1 + (key0 & 0xff)) * 134775813U + 1;
        key2 = crc32_byte(key2, key1 >> 24);
    }
    return key0 == 0x670e8462 && key1 == 0x306591b4 && key2 == 0x8372919d;
}

int main(int argc, char **argv) {
    if (argc != 2) {
        fprintf(stderr, "usage: %s WORDLIST\\n", argv[0]);
        return 2;
    }
    for (unsigned i = 0; i < 256; i++) {
        uint32_t value = i;
        for (unsigned bit = 0; bit < 8; bit++)
            value = (value >> 1) ^ ((value & 1) ? 0xedb88320 : 0);
        table[i] = value;
    }
    FILE *input = strcmp(argv[1], "-") == 0 ? stdin : fopen(argv[1], "rb");
    if (!input) return 2;
    char line[1024];
    size_t checked = 0;
    while (fgets(line, sizeof line, input)) {
        size_t length = strcspn(line, "\\r\\n");
        if (matches((const unsigned char *)line, length)) {
            printf("VERIFIED password=%.*s length=%zu\\n", (int)length, line, length);
            return 0;
        }
        checked++;
    }
    printf("NO_MATCH checked=%zu\\n", checked);
    return 1;
}
