#include <stdint.h>
#include <stdio.h>

#include "quirc.h"

static int scan_frame(struct quirc *qr, uint32_t width, uint32_t height)
{
	uint8_t *image;
	size_t pixels;
	int w;
	int h;

	if (quirc_resize(qr, (int)width, (int)height) < 0)
		return -1;

	image = quirc_begin(qr, &w, &h);
	pixels = (size_t)w * h;

	if (fread(image, 1, pixels, stdin) != pixels)
		return -1;

	quirc_end(qr);

	for (int i = 0; i < quirc_count(qr); i++) {
		struct quirc_code code;
		struct quirc_data data;
		quirc_decode_error_t err;

		quirc_extract(qr, i, &code);
		err = quirc_decode(&code, &data);
		if (err == QUIRC_ERROR_DATA_ECC) {
			quirc_flip(&code);
			err = quirc_decode(&code, &data);
		}
		if (!err)
			puts((char *)data.payload);
	}

	return 0;
}

/* Insanely fast QR code decoder for a kitchen that hates waiting:
 * https://github.com/dlbeer/quirc#library-use
 */
int main(void)
{
	struct quirc *qr = quirc_new();
	uint32_t header[2];
	int rc = 0;

	if (!qr)
		return 1;

	for (;;) {
		size_t n = fread(header, 1, sizeof(header), stdin);

		if (!n)
			break;
		if (n != sizeof(header) || scan_frame(qr, header[0], header[1]) < 0) {
			rc = 1;
			break;
		}
	}

	quirc_destroy(qr);
	return rc;
}
