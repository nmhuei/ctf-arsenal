import subprocess
import tempfile
from types import SimpleNamespace

from PIL import Image
from pyzbar.pyzbar import decode as decode_codes

from .config import DECODER_TIMEOUT, QRSCAN_ARGV, QRSCAN_DIR
from .image import ERROR, write_image
from .job import prepare_job


def decode_upload(upload, values):
    job = prepare_job(upload, values)
    if job.station == "kitchen":
        return job.image.name, kitchen_scan(job)
    return job.image.name, guest_scan(job)


def guest_scan(job):
    try:
        job.image.item.stream.seek(0)
        image = Image.open(job.image.item.stream)
        text = "\n".join(code.data.decode("utf-8", "replace") for code in decode_codes(image))
        return result((text + "\n") if text else "")
    except Exception as exc:
        raise ValueError(ERROR) from exc


def kitchen_scan(job):
    with tempfile.TemporaryFile() as stream:
        job.image.write_to(stream, write_image)
        stream.seek(0)
        return subprocess.run(
            QRSCAN_ARGV,
            stdin=stream,
            cwd=QRSCAN_DIR,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=DECODER_TIMEOUT,
            check=False,
        )


def result(output="", error="", returncode=0):
    return SimpleNamespace(
        stdout=output.encode(),
        stderr=error.encode(),
        returncode=returncode,
    )
