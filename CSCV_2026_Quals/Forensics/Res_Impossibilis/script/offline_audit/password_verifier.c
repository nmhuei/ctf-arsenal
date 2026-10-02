#include <stdint.h>
#include <stddef.h>
static uint32_t tab[256];
void setup(void) {
    for(unsigned i=0;i<256;i++) {
        uint32_t v=i;
        for(unsigned j=0;j<8;j++)v=(v>>1)^((v&1)?0xedb88320:0);
        tab[i]=v;
    }
}
static uint32_t crc(uint32_t x,unsigned char b){return (x>>8)^tab[(x^b)&255];}
int check_password(const unsigned char *p,size_t n) {
    uint32_t x=0x12345678,y=0x23456789,z=0x34567890;
    for(size_t i=0;i<n;i++) {
        x=crc(x,p[i]); y=(y+(x&255))*134775813U+1; z=crc(z,y>>24);
    }
    return x==0x670e8462U && y==0x306591b4U && z==0x8372919dU;
}
int find_password(const unsigned char *p,size_t n,size_t *start,size_t *length) {
    for(size_t i=0;i<n;i++) {
        uint32_t x=0x12345678;
        for(size_t j=i;j<n && j<i+128;j++) {
            x=crc(x,p[j]);
            if(x==0x670e8462U && check_password(p+i,j-i+1)) {
                *start=i; *length=j-i+1; return 1;
            }
        }
    }
    return 0;
}
int xor_family(const unsigned char *cipher,size_t n,unsigned keylen,uint64_t particular,
               const uint64_t *basis,unsigned freebits,unsigned char *output,uint64_t *foundkey) {
    if(n>128 || keylen>8 || freebits>24) return -1;
    unsigned char plain[128];
    uint64_t key=particular,limit=1ULL<<freebits;
    for(uint64_t i=0;i<limit;i++) {
        if(i) key^=basis[__builtin_ctzll(i)];
        int printable=1;
        for(size_t j=0;j<n;j++) {
            plain[j]=cipher[j]^((key>>(8*(j%keylen)))&255);
            if(plain[j]<32 || plain[j]>126){printable=0;break;}
        }
        if(printable && check_password(plain,n)) {
            for(size_t j=0;j<n;j++)output[j]=plain[j];
            *foundkey=key;return 1;
        }
    }
    return 0;
}
