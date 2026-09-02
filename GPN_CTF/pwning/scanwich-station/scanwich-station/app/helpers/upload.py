from werkzeug.utils import secure_filename


ERROR = "Choose an image before scanning."


def prepare_upload(upload):
    return Upload(upload)


class Upload:
    def __init__(self, item):
        self.item = item
        self.name = checked_name(item)

    def write_to(self, out, write):
        self.item.stream.seek(0)
        write(self.item.stream, out)


def checked_name(upload):
    filename = secure_filename(upload.filename if upload else "")
    if not filename:
        raise ValueError(ERROR)
    return filename
