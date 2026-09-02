from dataclasses import dataclass

from .upload import prepare_upload


@dataclass
class ScanJob:
    image: object
    station: str = "guest"


def prepare_job(upload, values):
    return ScanJob(prepare_upload(upload), **values)
