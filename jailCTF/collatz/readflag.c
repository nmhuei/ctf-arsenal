#include <fcntl.h>
#include <string.h>
#include <unistd.h>

const char flag[] = {
#embed "flag.txt"
};

int main(int argc, char *argv[]) {
  if (argc != 2 || strcmp(argv[1], "please im begging you") != 0) {
    write(1, "ask politely :(\n", 16);
    return 1;
  }

  write(1, flag, sizeof(flag));
  return 0;
}
