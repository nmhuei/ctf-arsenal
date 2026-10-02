#include "../password_verifier.c"
#include <stdio.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <unistd.h>
#include <string.h>

/* Strict scalar UTF-8, printable ASCII, and common line separators. */
static unsigned scalar_length(const unsigned char *p, size_t n) {
    if (!n) return 0;
    unsigned a=p[0];
    if ((a>=32 && a<=126) || a==9 || a==10 || a==13) return 1;
    if (n>=2 && a>=0xc2 && a<=0xdf && p[1]>=0x80 && p[1]<=0xbf) return 2;
    if (n>=3 && a>=0xe0 && a<=0xef && p[1]>=0x80 && p[1]<=0xbf
        && p[2]>=0x80 && p[2]<=0xbf && !(a==0xe0 && p[1]<0xa0)
        && !(a==0xed && p[1]>=0xa0)) return 3;
    if (n>=4 && a>=0xf0 && a<=0xf4 && p[1]>=0x80 && p[1]<=0xbf
        && p[2]>=0x80 && p[2]<=0xbf && p[3]>=0x80 && p[3]<=0xbf
        && !(a==0xf0 && p[1]<0x90) && !(a==0xf4 && p[1]>=0x90)) return 4;
    return 0;
}

int main(int argc, char **argv) {
    if (argc<2 || argc>3 || (argc==3 && strcmp(argv[2],"--gaps"))) {
        fprintf(stderr,"usage: %s memory-image [--gaps]\n",argv[0]);return 2;
    }
    int gaps=(argc==3);
    int fd=open(argv[1],O_RDONLY);
    struct stat st;
    if(fd<0 || fstat(fd,&st))return 2;
    size_t n=st.st_size;
    const unsigned char *m=mmap(NULL,n,PROT_READ,MAP_PRIVATE,fd,0);
    if(m==MAP_FAILED)return 2;
    setup();
    size_t tested=0,tested_bytes=0,skipped_by_mode=0,hits=0,maximum_run=0;
    for(size_t i=0;i<n;) {
        size_t start=i;int unicode=0;
        unsigned k;
        while(i<n && (k=scalar_length(m+i,n-i))) {unicode|=(k>1);i+=k;}
        size_t len=i-start;
        if(unicode) {
            int original_scope=(len>=13 && len<=4096);
            if(gaps != original_scope) {
                size_t found=0,length=0;tested++;tested_bytes+=len;
                if(len>maximum_run)maximum_run=len;
                if(find_password(m+start,len,&found,&length)) {
                    hits++;
                    printf("MATCH offset=%zx length=%zu hex=",start+found,length);
                    for(size_t j=0;j<length;j++)printf("%02x",m[start+found+j]);
                    puts("");fflush(stdout);
                }
            } else skipped_by_mode++;
        }
        if(i<n)i++;
    }
    printf("{\"image_bytes\":%zu,\"gaps_mode\":%d,\"unicode_runs_checked\":%zu,\"run_bytes_checked\":%zu,"
           "\"unicode_runs_excluded_by_mode\":%zu,\"maximum_run_bytes\":%zu,\"maximum_password_bytes\":128,\"hits\":%zu}\n",
           n,gaps,tested,tested_bytes,skipped_by_mode,maximum_run,hits);
    munmap((void *)m,n);close(fd);return 0;
}
