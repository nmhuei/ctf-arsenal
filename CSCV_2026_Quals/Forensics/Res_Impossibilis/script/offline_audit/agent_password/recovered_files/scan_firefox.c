#include <stdio.h>
#include <stdint.h>
#include <string.h>
#include <fcntl.h>
#include <unistd.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <zlib.h>

struct target {unsigned index;size_t length;uint32_t crc;const char *name;};
static const struct target targets[]={
 {32,18,0x93a63aed,"shield-preference-experiments.json"},
 {33,939,0x6d062582,"containers.json"},
 {34,683,0x6df5e5fd,"handlers.json"},
 {35,204,0xdae4fd3d,"broadcast-listeners.json"},
 {36,1043,0xe16206f5,"SiteSecurityServiceState.txt"}
};

static void check(const unsigned char *m,size_t size,size_t pos,unsigned t,const char *outdir) {
 const struct target *r=targets+t;
 if(pos+r->length>size)return;
 if(crc32(0,m+pos,r->length)!=r->crc)return;
 char path[1024];snprintf(path,sizeof(path),"%s/%02u_%zx_%s",outdir,r->index,pos,r->name);
 FILE *f=fopen(path,"wb");if(!f)return;
 fwrite(m+pos,1,r->length,f);fclose(f);
 printf("{\"index\":%u,\"offset\":\"0x%zx\",\"length\":%zu,\"crc32\":\"%08x\",\"path\":\"%s\"}\n",
        r->index,pos,r->length,r->crc,path);fflush(stdout);
}

int main(int argc,char **argv) {
 if(argc!=3)return 2;
 int fd=open(argv[1],O_RDONLY);struct stat st;if(fd<0||fstat(fd,&st))return 2;
 size_t n=st.st_size;const unsigned char *m=mmap(NULL,n,PROT_READ,MAP_PRIVATE,fd,0);
 if(m==MAP_FAILED)return 2;
 size_t pos=0,json_starts=0,hsts_markers=0;
 while(pos<n) {
  const unsigned char *p=memchr(m+pos,'{',n-pos);if(!p)break;
  pos=(size_t)(p-m);json_starts++;
  for(unsigned t=0;t<4;t++)check(m,n,pos,t,argv[2]);
  pos++;
 }
 pos=0;
 while(pos<n) {
  const unsigned char *p=memchr(m+pos,':',n-pos);if(!p)break;
  pos=(size_t)(p-m);
  if(pos+6<=n && !memcmp(m+pos,":HSTS\t",6)) {
   hsts_markers++;size_t begin=pos;
   while(begin>0 && pos-begin<512 && m[begin-1]>=32 && m[begin-1]<=126)begin--;
   check(m,n,begin,4,argv[2]);
  }
  pos++;
 }
 fprintf(stderr,"image_bytes=%zu json_starts=%zu hsts_markers=%zu\n",n,json_starts,hsts_markers);
 munmap((void*)m,n);close(fd);return 0;
}
