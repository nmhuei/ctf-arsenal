#include <stdint.h>
#include <stddef.h>
static uint32_t table[256];
void setup(void){for(unsigned i=0;i<256;i++){uint32_t x=i;for(int j=0;j<8;j++)x=(x>>1)^((x&1)?0xedb88320:0);table[i]=x;}}
int verify(const unsigned char*p,size_t n){uint32_t a=0x6b5de7d7,b=0x488ec071,c=0xe6888511;for(size_t i=0;i<n;i++){a=(a>>8)^table[(a^p[i])&255];b=(b+(a&255))*134775813u+1;c=(c>>8)^table[(c^(b>>24))&255];}return a==0x7e644859&&b==0x845c6b3a&&c==0x6a1087cc;}
