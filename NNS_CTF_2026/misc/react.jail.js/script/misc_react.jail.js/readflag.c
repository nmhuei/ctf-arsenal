#include <stdio.h>
#include <string.h>

#ifndef FLAG
#define FLAG "NNS{REPLACE_ME}"
#endif

static const char *passphrase =
    "According to all known laws of aviation, there is no way that a bee "
    "should be able to FLY. Its wings are too small to get its fat "
    "little body off the ground. The bee, of course, flies anyways. "
    "Because BEES don't care what humans think is impossible.";

int main(int argc, char **argv) {
  if (argc != 2 || strcmp(argv[1], passphrase) != 0) {
    printf("Usage: %s \"%s\"\n", argv[0], passphrase);
    return 1;
  }

  puts(FLAG);
  return 0;
}
