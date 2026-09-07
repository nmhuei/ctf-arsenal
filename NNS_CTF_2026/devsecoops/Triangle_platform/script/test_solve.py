import pathlib
import sys
from unittest.mock import patch

sys.path.insert(0, str(pathlib.Path(__file__).parents[1]))

from solver.solve import (
    create_origin_alias,
    create_registry_token_secret,
    edge_site_yaml,
    origin_site_yaml,
    switch_to_origin,
)


def test_edge_yaml_uses_parser_differential_and_exposes_token():
    payload = edge_site_yaml()
    assert "integrations: [edge]" in payload
    assert "<<: *allowed" in payload
    assert "root: /var/run/triangle" in payload
    assert "index: token" in payload


def test_origin_yaml_reads_secret_key():
    payload = origin_site_yaml()
    assert "root: /var/run/origin" in payload
    assert "index: FLAG" in payload


def test_registry_secret_request_targets_triangle_system():
    with patch("solver.solve.request") as mocked:
        secret_name = create_registry_token_secret("tri-test", "edge-token")

    assert secret_name == "tri-test-registry-token"
    method, path = mocked.call_args.args[:2]
    kwargs = mocked.call_args.kwargs
    assert method == "POST"
    assert path == "/api/v1/namespaces/triangle-system/secrets"
    assert kwargs["token"] == "edge-token"
    assert kwargs["body"]["metadata"]["annotations"][
        "kubernetes.io/service-account.name"
    ] == "tri-registry-sync"


def test_origin_alias_and_patch_use_verified_values():
    with patch("solver.solve.request") as mocked:
        create_origin_alias("tri-test", "registry-token")
        switch_to_origin("tri-test")

    alias_call, patch_call = mocked.call_args_list
    assert alias_call.kwargs["body"]["spec"]["host"] == "ACME-invoices.sites.triangle.tld"
    assert alias_call.kwargs["body"]["spec"]["siteRef"] == {
        "namespace": "tenant-a",
        "name": "tri-test",
    }
    assert patch_call.args[:2] == (
        "PATCH",
        "/apis/triangle.io/v1/namespaces/tenant-a/sites/tri-test",
    )
    assert patch_call.kwargs["content_type"] == "application/merge-patch+json"
