#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
static uint32_t tab[256];static size_t strings,count;
static uint32_t crc(uint32_t x,unsigned char c){return (x>>8)^tab[(x^c)&255];}
static void upd(uint32_t*k,unsigned char c){k[0]=crc(k[0],c);k[1]=(k[1]+(k[0]&255))*134775813U+1;k[2]=crc(k[2],k[1]>>24);}
static void check(const unsigned char*p,size_t n,size_t off){
 if(n<12||n>128)return;strings++;
 for(size_t i=0;i+12<=n;i++){
  uint32_t k[3]={0x12345678,0x23456789,0x34567890};
  for(size_t j=i;j<n&&j<i+80;j++){
   upd(k,p[j]);count++;
   if(k[0]==0x670e8462U&&k[1]==0x306591b4U&&k[2]==0x8372919dU){
    printf("VERIFIED offset=%zx password=%.*s\n",off+i,(int)(j-i+1),p+i);fflush(stdout);
    FILE*f=fopen("script/offline_audit/archive_password.txt","wb");fwrite(p+i,1,j-i+1,f);fclose(f);exit(0);
   }
  }
 }
}
int main(){for(unsigned i=0;i<256;i++){uint32_t c=i;for(int j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320:0);tab[i]=c;}
 int fd=open("script/evidence/mem.clean",O_RDONLY);struct stat st;fstat(fd,&st);unsigned char*m=mmap(0,st.st_size,PROT_READ,MAP_PRIVATE,fd,0);size_t start=0;
 for(size_t i=0;i<(size_t)st.st_size;i++){if(m[i]>=32&&m[i]<=126)continue;if(i>start)check(m+start,i-start,start);start=i+1;}
 printf("Checked %zu strings, %zu key updates\n",strings,count);return 0;
}
