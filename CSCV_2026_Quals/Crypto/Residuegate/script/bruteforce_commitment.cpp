#include <array>
#include <cstdint>
#include <cstdio>
#include <cstring>
#include <openssl/sha.h>
#include <string>
#include <vector>

// Local verifier for the stated six-way commitment.  The 16 rows are the
// logits reconstructed from the supplied cache for base_badge.png.
static constexpr int64_t logits[16][4] = {
    {59,-102,308,40},{89,-89,323,17},{109,-62,173,172},{100,-117,238,88},
    {92,-51,144,150},{91,-45,197,84},{76,-75,156,168},{96,-62,253,132},
    {89,-60,180,78},{67,-42,248,40},{72,-108,161,47},{90,-98,223,87},
    {64,-70,162,148},{102,-85,196,-8},{53,-56,178,85},{66,-128,191,28},
};
static constexpr int64_t mixing[4][4] = {
    {1,1,0,1}, {0,1,1,-1}, {1,0,1,1}, {1,-1,1,0},
};

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
        std::fprintf(stderr, "usage: %s <seed-hex> <commitment-hex> <domain> <logit-mode>\n", argv[0]);
        return 2;
    }
    uint8_t seed[32], target[32];
    if (std::strlen(argv[1]) != 64 || std::strlen(argv[2]) != 64 ||
        !hex_to_bytes(argv[1], seed, 32) || !hex_to_bytes(argv[2], target, 32)) {
        std::fputs("seed and commitment must each be 64 hex characters\n", stderr);
        return 2;
    }
    const std::string domain(argv[3]);
    const int mode = std::atoi(argv[4]);
    if (mode < 0 || mode > 2) {
        std::fputs("logit-mode: 0=raw, 1=M*raw, 2=M^T*raw\n", stderr);
        return 2;
    }
    std::vector<uint8_t> message(domain.begin(), domain.end());
    // The runtime hashes the C-string domain, including its NUL terminator.
    message.push_back(0);
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
            int64_t values[4];
            for (int cls = 0; cls < 4; ++cls) {
                values[cls] = mode == 0 ? logits[variant][cls] : 0;
                if (mode != 0) {
                    for (int k = 0; k < 4; ++k) {
                        values[cls] += (mode == 1 ? mixing[cls][k] : mixing[k][cls]) * logits[variant][k];
                    }
                }
                put_i64_le(at, values[cls]);
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
