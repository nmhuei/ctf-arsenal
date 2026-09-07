import gzip
import hashlib
import io
import json
import tarfile

from solver.solve import extract_flag, page_tag, manifest_layers


def test_page_tag_matches_builder_content_hash():
    assert page_tag("x") == "2d711642b726"


def test_manifest_layers_reads_docker_v2_layer_digests():
    manifest = {
        "schemaVersion": 2,
        "config": {"digest": "sha256:config"},
        "layers": [
            {"digest": "sha256:first", "size": 10},
            {"digest": "sha256:last", "size": 20},
        ],
    }
    assert manifest_layers(manifest) == ["sha256:first", "sha256:last"]


def test_extract_flag_reads_flag_from_a_compressed_image_layer():
    tar_buffer = io.BytesIO()
    with tarfile.open(fileobj=tar_buffer, mode="w") as archive:
        payload = b"the secret is FLAG{layer_secret_123}\n"
        member = tarfile.TarInfo("usr/share/nginx/html/flag.txt")
        member.size = len(payload)
        archive.addfile(member, io.BytesIO(payload))

    layer = gzip.compress(tar_buffer.getvalue(), mtime=0)
    assert extract_flag(layer) == "FLAG{layer_secret_123}"


def test_extract_flag_accepts_the_nns_flag_prefix():
    assert extract_flag(b"NNS{builder_secret_123}") == "NNS{builder_secret_123}"
