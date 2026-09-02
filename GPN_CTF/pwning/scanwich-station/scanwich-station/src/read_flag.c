#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int main(void)
{
	char buf[256];
	ssize_t n;
	int fd;

	if (setgid(0) || setuid(0))
		return 1;

	fd = open("/flag", O_RDONLY);
	if (fd < 0) {
		perror("open /flag");
		return 1;
	}

	while ((n = read(fd, buf, sizeof(buf))) > 0) {
		ssize_t off = 0;

		while (off < n) {
			ssize_t written = write(STDOUT_FILENO, buf + off, n - off);

			if (written <= 0) {
				perror("write");
				close(fd);
				return 1;
			}
			off += written;
		}
	}

	if (n < 0) {
		perror("read /flag");
		close(fd);
		return 1;
	}

	close(fd);
	return 0;
}
