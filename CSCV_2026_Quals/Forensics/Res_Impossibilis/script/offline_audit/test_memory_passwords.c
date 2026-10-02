#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
#include <string.h>
static uint32_t tab[256];static unsigned char enc[851];static size_t count;
static uint32_t crc(uint32_t x,unsigned char c){return (x>>8)^tab[(x^c)&255];}
static void upd(uint32_t *k,unsigned char c){k[0]=crc(k[0],c);k[1]=(k[1]+(k[0]&255))*134775813U+1;k[2]=crc(k[2],k[1]>>24);}
static unsigned char dec(uint32_t*k,unsigned char c){unsigned t=(k[2]&65535)|2;unsigned char b=c^((t*(t^1))>>8);upd(k,b);return b;}
static void test(const unsigned char*p,size_t n,size_t offset){
 if(n<6||n>128)return;count++;uint32_t k[3]={0x12345678,0x23456789,0x34567890};
 for(size_t i=0;i<n;i++)upd(k,p[i]);unsigned char b=0;
 for(int i=0;i<12;i++)b=dec(k,enc[i]);if(b!=0x58)return;
 uint32_t c=0xffffffff;unsigned char data[839];for(int i=12;i<851;i++){data[i-12]=dec(k,enc[i]);c=crc(c,data[i-12]);}
 if((c^0xffffffff)!=1491389140U)return;
 printf("VERIFIED offset=%zx password=%.*s\n",offset,(int)n,p);fflush(stdout);
 FILE *f=fopen("script/offline_audit/first_document.txt","wb");fwrite(data,1,839,f);fclose(f);
 f=fopen("script/offline_audit/archive_password.txt","wb");fwrite(p,1,n,f);fclose(f);
}
int main(){
 for(unsigned i=0;i<256;i++){uint32_t c=i;for(int j=0;j<8;j++)c=(c>>1)^((c&1)?0xedb88320:0);tab[i]=c;}
 FILE*f=fopen("script/offline_audit/mega_archive_2f3e054.bin","rb");fseek(f,66,SEEK_SET);fread(enc,1,851,f);fclose(f);
 int fd=open("script/evidence/mem.clean",O_RDONLY);struct stat st;fstat(fd,&st);unsigned char*m=mmap(0,st.st_size,PROT_READ,MAP_PRIVATE,fd,0);size_t start=0;
 for(size_t i=0;i<(size_t)st.st_size;i++){if(m[i]>=33&&m[i]<=126)continue;if(i>start)test(m+start,i-start,start);start=i+1;}
 printf("Checked %zu candidates\n",count);munmap(m,st.st_size);close(fd);return 0;
}
