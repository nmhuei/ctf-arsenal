#!/usr/bin/env python3
"""Behavior tests for the network-capture solver."""

from solver import solve


def test_extract_flag_ignores_decoy_flag_formats():
    capture = """
    10.10.10.20.40700 > 10.10.10.99.1337: FLAG{decoy}
    10.10.10.10.80 > 10.10.10.20.40700: HTTP/1.1 200 OK
    NNS{sw17ch3D_n3tW0RK5_still_tRU5t_aRP_so_K3ep_y0Ur_deviC3s_53Parate}
    """
    extractor = getattr(solve, "extract_flag", None)
    assert extractor is not None, "solver must expose extract_flag"
    assert extractor(capture) == (
        "NNS{sw17ch3D_n3tW0RK5_still_tRU5t_aRP_so_K3ep_y0Ur_deviC3s_53Parate}"
    )


def test_extract_flag_rejects_ambiguous_candidates():
    capture = "NNS{first}\nNNS{second}\n"
    extractor = getattr(solve, "extract_flag", None)
    assert extractor is not None, "solver must expose extract_flag"
    try:
        extractor(capture)
    except RuntimeError as error:
        assert "ambiguous" in str(error).lower()
    else:
        raise AssertionError("multiple candidates must not be accepted")
