#include <stdio.h>

int main(int argc, char **argv) {
    if (argc >= 4) {
        puts(argv[3]);
        return 0;
    }

    fputs("missing flag\n", stderr);
    return 1;
}
