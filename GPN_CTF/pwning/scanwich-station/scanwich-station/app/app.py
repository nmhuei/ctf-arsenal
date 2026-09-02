#!/usr/bin/env python3
from flask import Flask, Response, render_template, request

from helpers.config import MAX_CONTENT_LENGTH
from helpers.decoder import decode_upload


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH


@app.get("/")
def index():
    return render_template("index.html")


@app.post("/scan")
def scan():
    try:
        filename, result = decode_upload(request.files.get("image"), request.form.to_dict())
    except Exception as exc:
        return render_error(str(exc), 400)

    output = result.stdout.decode("utf-8", "replace")
    error = result.stderr.decode("utf-8", "replace")
    if request.args.get("raw") == "1":
        return Response(output + error, mimetype="text/plain")

    return render_template(
        "result.html",
        filename=filename,
        output=output,
        error=error,
        returncode=result.returncode,
    )


def render_error(message, status):
    if request.args.get("raw") == "1":
        return Response(message + "\n", status=status, mimetype="text/plain")
    return render_template(
        "result.html",
        message=message,
        status="blocked",
    ), status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, threaded=True)
