#include "../password_verifier.c"
void derive_exact_keys(const unsigned char *p, size_t n, uint32_t out[3]) {
    uint32_t x=0x12345678,y=0x23456789,z=0x34567890;
    for(size_t i=0;i<n;i++) {
        x=crc(x,p[i]);y=(y+(x&255))*134775813U+1;z=crc(z,y>>24);
    }
    out[0]=x;out[1]=y;out[2]=z;
}
