#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <openssl/sha.h>
#include <string>
#include <vector>

static bool hex_to_bytes(const char *hex, uint8_t *out, size_t n) {
    for (size_t i = 0; i < n; ++i) {
        unsigned x;
        if (std::sscanf(hex + 2 * i, "%2x", &x) != 1) return false;
        out[i] = static_cast<uint8_t>(x);
    }
    return true;
}

static void put_i64_le(uint8_t *out, int64_t value) {
    uint64_t u = static_cast<uint64_t>(value);
    for (int i = 0; i < 8; ++i) out[i] = static_cast<uint8_t>(u >> (8 * i));
}

int main(int argc, char **argv) {
    if (argc != 5) {
        std::fprintf(stderr, "usage: %s <seed-hex> <commitment-hex> <domain> <logits-txt-file>\n", argv[0]);
        return 2;
    }
    uint8_t seed[32], target[32];
    if (std::strlen(argv[1]) != 64 || std::strlen(argv[2]) != 64 ||
        !hex_to_bytes(argv[1], seed, 32) || !hex_to_bytes(argv[2], target, 32)) {
        std::fputs("seed and commitment must each be 64 hex characters\n", stderr);
        return 2;
    }
    const std::string domain(argv[3]);
    const char *logits_file = argv[4];

    int64_t logits[6][16][4];
    FILE *f = std::fopen(logits_file, "r");
    if (!f) {
        std::fprintf(stderr, "cannot open logits file: %s\n", logits_file);
        return 2;
    }
    for (int s = 0; s < 6; ++s) {
        for (int v = 0; v < 16; ++v) {
            for (int c = 0; c < 4; ++c) {
                long long val;
                if (std::fscanf(f, "%lld", &val) != 1) {
                    std::fprintf(stderr, "error reading logit at slot %d var %d cls %d\n", s, v, c);
                    std::fclose(f);
                    return 2;
                }
                logits[s][v][c] = val;
            }
        }
    }
    std::fclose(f);

    std::vector<uint8_t> message(domain.begin(), domain.end());
    message.push_back(0); // NUL terminator
    message.insert(message.end(), seed, seed + 32);
    const size_t prefix = message.size();
    message.resize(prefix + 6 * 34);
    uint8_t digest[SHA256_DIGEST_LENGTH];

    for (uint32_t packed = 0; packed < (1u << 24); ++packed) {
        uint32_t state = packed;
        uint8_t *at = message.data() + prefix;
        uint8_t variants[6];
        for (uint8_t slot = 0; slot < 6; ++slot) {
            uint8_t variant = static_cast<uint8_t>(state & 15);
            state >>= 4;
            variants[slot] = variant;
            *at++ = slot;
            *at++ = variant;
            for (int cls = 0; cls < 4; ++cls) {
                put_i64_le(at, logits[slot][variant][cls]);
                at += 8;
            }
        }
        SHA256(message.data(), message.size(), digest);
        if (std::memcmp(digest, target, 32) == 0) {
            std::printf("match: [%u,%u,%u,%u,%u,%u]\n", variants[0], variants[1], variants[2], variants[3], variants[4], variants[5]);
            return 0;
        }
    }
    std::puts("no match");
    return 1;
}
