#include "password_verifier.c"
#include <stdio.h>
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <unistd.h>
static int decode[256];
static size_t scanned,low7_count;
static FILE *candidates;
static void inspect(unsigned char *data,size_t n,size_t offset,const char *encoding) {
    size_t start=0,length=0;
    if(find_password(data,n,&start,&length)) {
        printf("VERIFIED %s offset=%zx password=%.*s\n",encoding,offset,(int)length,data+start);
        FILE *f=fopen("script/offline_audit/archive_password.txt","wb");
        fwrite(data+start,1,length,f);fclose(f);exit(0);
    }
    if(n<20||n>128)return;
    for(size_t i=0;i<n;i++)if(data[i]&128)return;
    low7_count++;
    fprintf(candidates,"%zx\t%s\t",offset,encoding);
    for(size_t i=0;i<n;i++)fprintf(candidates,"%02x",data[i]);
    fputc('\n',candidates);
}
static void check(const unsigned char *data,size_t n,size_t offset) {
    if(n<16||n>256)return;
    scanned++;
    unsigned char result[256];size_t length=0;unsigned acc=0,bits=0;
    if(n%4!=1) {
        for(size_t i=0;i<n;i++) {
            int v=decode[data[i]];
            if(v<0)break;
            acc=(acc<<6)|v;bits+=6;
            if(bits>=8){bits-=8;result[length++]=(acc>>bits)&255;}
        }
        inspect(result,length,offset,"base64");
    }
    if(n%2==0) {
        length=0;
        for(size_t i=0;i<n;i+=2) {
            int a=data[i]>='0'&&data[i]<='9'?data[i]-'0':
                  data[i]>='a'&&data[i]<='f'?data[i]-'a'+10:
                  data[i]>='A'&&data[i]<='F'?data[i]-'A'+10:-1;
            int b=data[i+1]>='0'&&data[i+1]<='9'?data[i+1]-'0':
                  data[i+1]>='a'&&data[i+1]<='f'?data[i+1]-'a'+10:
                  data[i+1]>='A'&&data[i+1]<='F'?data[i+1]-'A'+10:-1;
            if(a<0||b<0)return;
            result[length++]=(a<<4)|b;
        }
        inspect(result,length,offset,"hex");
    }
}
int main(void) {
    setup();for(unsigned i=0;i<256;i++)decode[i]=-1;
    const char *alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    for(unsigned i=0;i<64;i++)decode[(unsigned char)alphabet[i]]=i;
    decode['-']=62;decode['_']=63;
    int fd=open("script/evidence/mem.clean",O_RDONLY);struct stat st;
    if(fd<0||fstat(fd,&st))return 2;
    const unsigned char *m=mmap(NULL,st.st_size,PROT_READ,MAP_PRIVATE,fd,0);
    if(m==MAP_FAILED)return 2;
    candidates=fopen("script/offline_audit/encoded_low7_candidates.tsv","w");
    size_t start=0;
    for(size_t i=0;i<(size_t)st.st_size;i++) {
        if(decode[m[i]]>=0)continue;
        if(i>start)check(m+start,i-start,start);
        start=i+1;
    }
    check(m+start,st.st_size-start,start);fclose(candidates);
    printf("Encoded tokens checked=%zu; low7 candidates=%zu; no verified password\n",scanned,low7_count);
    return 0;
}
