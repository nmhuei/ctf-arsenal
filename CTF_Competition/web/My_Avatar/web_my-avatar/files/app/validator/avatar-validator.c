#include <avif/avif.h>

#include <stdint.h>
#include <stdio.h>
#include <sys/resource.h>

#define MAX_AVATAR_WIDTH 512U
#define MAX_AVATAR_HEIGHT 512U
#define MIN_AVATAR_WIDTH 64U
#define MIN_AVATAR_HEIGHT 64U
#define MAX_AVATAR_PIXELS (MAX_AVATAR_WIDTH * MAX_AVATAR_HEIGHT)
#define MAX_CPU_SECONDS 3U

static int apply_resource_limits(void)
{
    const struct rlimit cpuTime = {
        .rlim_cur = MAX_CPU_SECONDS,
        .rlim_max = MAX_CPU_SECONDS,
    };
    const struct rlimit coreSize = {
        .rlim_cur = 0,
        .rlim_max = 0,
    };

    return setrlimit(RLIMIT_CPU, &cpuTime) == 0 &&
           setrlimit(RLIMIT_CORE, &coreSize) == 0;
}

int main(int argc, char **argv)
{
    if (argc != 2 || !apply_resource_limits()) {
        return 2;
    }

    avifDecoder *decoder = avifDecoderCreate();
    avifImage *image = avifImageCreateEmpty();
    if (decoder == NULL || image == NULL) {
        avifDecoderDestroy(decoder);
        avifImageDestroy(image);
        return 2;
    }

    decoder->codecChoice = AVIF_CODEC_CHOICE_DAV1D;
    decoder->maxThreads = 1;
    decoder->imageSizeLimit = MAX_AVATAR_PIXELS;
    decoder->imageDimensionLimit = MAX_AVATAR_WIDTH;
    decoder->imageCountLimit = 1;

    const avifResult result = avifDecoderReadFile(decoder, image, argv[1]);
    if (result != AVIF_RESULT_OK) {
        fprintf(stderr, "AVIF validation failed: %s\n", avifResultToString(result));
        avifDecoderDestroy(decoder);
        avifImageDestroy(image);
        return 1;
    }

    const uint32_t width = image->width;
    const uint32_t height = image->height;
    avifDecoderDestroy(decoder);
    avifImageDestroy(image);

    if (width < MIN_AVATAR_WIDTH || height < MIN_AVATAR_HEIGHT ||
        width > MAX_AVATAR_WIDTH || height > MAX_AVATAR_HEIGHT) {
        return 1;
    }

    return 0;
}
