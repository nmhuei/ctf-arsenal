#define _GNU_SOURCE
#include <dlfcn.h>
#include <string.h>
#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
static int (*real_unlink)(const char*) = 0;
static int (*real_unlinkat)(int,const char*,int) = 0;
int unlink(const char *path){
    if(!real_unlink) real_unlink=dlsym(RTLD_NEXT,"unlink");
    if(path && (strstr(path,"flag.txt.emilia") || strstr(path,"_Rem.cab"))){ fprintf(stderr,"[no_unlink] keep %s\n",path); return 0; }
    return real_unlink(path);
}
int unlinkat(int dirfd, const char *path, int flags){
    if(!real_unlinkat) real_unlinkat=dlsym(RTLD_NEXT,"unlinkat");
    if(path && (strstr(path,"flag.txt.emilia") || strstr(path,"_Rem.cab"))){ fprintf(stderr,"[no_unlinkat] keep %s\n",path); return 0; }
    return real_unlinkat(dirfd,path,flags);
}
