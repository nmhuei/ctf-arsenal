
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

uint64_t fake_chunk[10] __attribute__((aligned(16)));

int main() {
    fake_chunk[0] = 0;
    fake_chunk[1] = 0x71; // size = 0x70, PREV_INUSE = 1
    void *ptr = &fake_chunk[2];
    printf("Testing free(%p)...\n", ptr);
    free(ptr);
    printf("free() succeeded! Now testing malloc(0x64)...\n");
    void *p = malloc(0x64);
    printf("malloc(0x64) returned: %p\n", p);
    return 0;
}
