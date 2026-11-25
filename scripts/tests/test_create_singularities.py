"""Tests for the helpers of scripts/create_singularities

Run with `nox -e test` under scripts/ .
"""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
import json
from pathlib import Path
import sys
from typing import Any, Optional

import pytest
import requests

SCRIPT = Path(__file__).parent.parent / "create_singularities"
loader = SourceFileLoader("create_singularities", str(SCRIPT))
spec = spec_from_loader(loader.name, loader)
assert spec is not None
cs = module_from_spec(spec)
# dataclasses need to find the module while it is being loaded
sys.modules[loader.name] = cs
loader.exec_module(cs)


def tag(name: str, *archs: str) -> dict[str, Any]:
    return {
        "name": name,
        "images": [{"architecture": a, "os": "linux"} for a in archs],
    }


@pytest.mark.parametrize(
    "t,expected",
    [
        ("26.1.1", ("26.1.1", None)),
        ("26.1.1-arm64", ("26.1.1", "arm64")),
        ("26.1.1-amd64", ("26.1.1", "amd64")),
        ("26.0.0rc1-arm64", ("26.0.0rc1", "arm64")),
        ("v1.0_x86_64", ("v1.0", "amd64")),
        ("1.0-AArch64", ("1.0", "arm64")),
        ("1.0-arm64v8", ("1.0", "arm64")),
        ("1.2.386", ("1.2.386", None)),
        ("1.2-386", ("1.2-386", None)),
        ("1.2-i386", ("1.2", "386")),
        ("latest", ("latest", None)),
        ("arm64", ("arm64", None)),
    ],
)
def test_split_arch_suffix(t: str, expected: tuple[str, Optional[str]]) -> None:
    assert cs.split_arch_suffix(t) == expected


# What https://hub.docker.com/r/nipreps/mriqc/tags looked like when we
# mistakenly switched to arm64 images
MRIQC_TAGS = [
    tag("latest", "amd64", "arm64"),
    tag("26.1.1", "amd64", "arm64"),
    tag("26.1.1-arm64", "arm64", "unknown"),
    tag("26.1.1-amd64", "amd64", "unknown"),
    tag("26.1.0", "amd64", "arm64"),
    tag("26.1.0-arm64", "arm64", "unknown"),
    tag("26.1.0-amd64", "amd64", "unknown"),
    tag("26.0.0rc1", "amd64", "arm64"),
    tag("26.0.0rc1-arm64", "arm64", "unknown"),
    tag("26.0.0rc1-amd64", "amd64", "unknown"),
]


@pytest.mark.parametrize(
    "tags,kwargs,expected",
    [
        (MRIQC_TAGS, {}, ("26.1.1", "26.1.1")),
        (MRIQC_TAGS[::-1], {}, ("26.1.1", "26.1.1")),
        (MRIQC_TAGS, {"arch": "arm64"}, ("26.1.1", "26.1.1")),
        # no multi-arch tag -- take the one explicitly for our architecture
        # but do not carry architecture into the version
        (
            [tag("1.1-arm64", "arm64"), tag("1.1-amd64", "amd64"), tag("1.0", "amd64")],
            {},
            ("1.1", "1.1-amd64"),
        ),
        # the same if Docker Hub does not tell architectures
        ([tag("1.1-arm64"), tag("1.1-amd64"), tag("1.0")], {}, ("1.1", "1.1-amd64")),
        # do not switch to a newer release until it has our architecture
        (
            [tag("2.0-arm64", "arm64"), tag("1.0-arm64", "arm64"), tag("1.0", "amd64")],
            {},
            ("1.0", "1.0"),
        ),
        ([tag("2.0", "arm64"), tag("1.0", "amd64", "arm64")], {}, ("1.0", "1.0")),
        # pre-releases are not hidden by the architecture suffix
        ([tag("2.0rc1-amd64", "amd64"), tag("1.0", "amd64")], {}, ("1.0", "1.0")),
        ([tag("2.0rc1-arm64"), tag("2.0a1"), tag("master")], {}, None),
        # nothing for our architecture at all
        ([tag("2.0-arm64", "arm64"), tag("1.0-arm64", "arm64")], {}, None),
        ([tag("2.0-arm64", "arm64")], {}, None),
        # prefixes of the versions
        ([tag("v1.2.3", "amd64"), tag("v1.10.0", "amd64")], {}, ("1.10.0", "v1.10.0")),
        # a single tag is taken as is, unless only good versions requested
        ([tag("latest", "amd64")], {}, ("latest", "latest")),
        ([tag("latest", "amd64")], {"only_good_versions": True}, None),
        ([tag("1.0", "amd64")], {"only_good_versions": True}, ("1.0", "1.0")),
        ([], {}, None),
        # version_regex
        (
            [tag("21.0.1"), tag("20.2.7"), tag("20.2.7-arm64"), tag("20.2.6")],
            {"version_regex": r"^v?20\.2\.[0-9]+$"},
            ("20.2.7", "20.2.7"),
        ),
        # version_regex is matched against the tag without architecture
        (
            [tag("20.2.7-amd64"), tag("20.2.7-arm64"), tag("20.2.6")],
            {"version_regex": r"^v?20\.2\.[0-9]+$"},
            ("20.2.7", "20.2.7-amd64"),
        ),
        # multi-arch tag lacks our architecture, but there is explicit one
        ([tag("1.1", "arm64"), tag("1.1-amd64", "amd64")], {}, ("1.1", "1.1-amd64")),
        ([tag("1.1-amd64", "amd64"), tag("1.1", "arm64")], {}, ("1.1", "1.1-amd64")),
        # architecture not in the suffix, but Docker Hub tells
        ([tag("2.0-arm64-gpu", "arm64"), tag("1.0", "amd64")], {}, ("1.0", "1.0")),
        # single tag with architecture
        ([tag("1.0-amd64", "amd64")], {}, ("1.0", "1.0-amd64")),
        ([tag("latest"), tag("2.0-arm64")], {}, None),
        # only Linux images count
        (
            [
                {"name": "2.0", "images": [{"architecture": "amd64", "os": "windows"}]},
                tag("1.0", "amd64"),
            ],
            {},
            ("1.0", "1.0"),
        ),
        # no information on images
        ([{"name": "1.1", "images": None}, {"name": "1.0"}], {}, ("1.1", "1.1")),
        # unknown architecture alone does not disqualify
        ([tag("1.1", "unknown"), tag("1.0", "amd64")], {}, ("1.1", "1.1")),
    ],
)
def test_select_last_version_tag(
    tags: list[dict[str, Any]],
    kwargs: dict[str, Any],
    expected: Optional[tuple[str, str]],
) -> None:
    assert cs.select_last_version_tag(tags, "some/image", **kwargs) == expected


@pytest.mark.parametrize(
    "tags,version_tag,kwargs,expected",
    [
        (MRIQC_TAGS, "26.1.1", {}, {"arm64": "26.1.1-arm64"}),
        (MRIQC_TAGS, "26.1.0", {}, {"arm64": "26.1.0-arm64"}),
        (MRIQC_TAGS, "26.1.1-amd64", {}, {"arm64": "26.1.1-arm64"}),
        (MRIQC_TAGS, "26.1.1", {"arch": "arm64"}, {"amd64": "26.1.1-amd64"}),
        (MRIQC_TAGS, "latest", {}, {}),
        # only explicitly tagged ones, and only of the same version
        ([tag("1.0", "amd64", "arm64"), tag("0.9-arm64", "arm64")], "1.0", {}, {}),
        (
            [tag("v1.0"), tag("v1.0-aarch64"), tag("v1.0_arm64"), tag("v1.0-s390x")],
            "v1.0",
            {},
            {"arm64": "v1.0-aarch64", "s390x": "v1.0-s390x"},
        ),
        # name of the tag does not match what Docker Hub tells
        ([tag("1.0", "amd64"), tag("1.0-arm64", "amd64")], "1.0", {}, {}),
    ],
)
def test_select_other_arch_tags(
    tags: list[dict[str, Any]],
    version_tag: str,
    kwargs: dict[str, Any],
    expected: dict[str, str],
) -> None:
    assert cs.select_other_arch_tags(tags, version_tag, **kwargs) == expected


@pytest.mark.parametrize(
    "repoid,expected",
    [
        ("nipreps/fmriprep", "bids-fmriprep--1.0"),
        ("pennlinc/toy_bids_app", "bids-toy-bids-app--1.0"),
        ("ghcr.io/unfmontreal/skullduggery", "bids-skullduggery--1.0"),
        ("afni", "bids-afni--1.0"),
    ],
)
def test_get_imagename(repoid: str, expected: str) -> None:
    assert cs.get_imagename(repoid, "bids", "1.0") == expected


def response(url: str, status: int, body: Any = None, **headers: str) -> requests.Response:
    r = requests.Response()
    r.url, r.status_code = url, status
    r._content = json.dumps(body).encode()
    r.headers.update(headers)
    return r


@pytest.mark.parametrize("auth", [True, False])
def test_get_oci_tag_records(monkeypatch: pytest.MonkeyPatch, auth: bool) -> None:
    pages = {
        "": ({"tags": ["1.0", "latest"]}, '</v2/o/i/tags/list?last=latest&n=2>; rel="next"'),
        "?last=latest&n=2": ({"tags": ["1.1-arm64"]}, ""),
    }

    def get(url: str, headers: Any = None, params: Any = None) -> requests.Response:
        if url == "https://ghcr.io/token":
            assert params == {"service": "ghcr.io", "scope": "repository:o/i:pull"}
            return response(url, 200, {"token": "T"})
        if auth and headers != {"Authorization": "Bearer T"}:
            challenge = 'Bearer realm="https://ghcr.io/token",service="ghcr.io",scope="repository:o/i:pull"'
            return response(url, 401, **{"www-authenticate": challenge})
        body, link = pages[url.removeprefix("https://ghcr.io/v2/o/i/tags/list")]
        return response(url, 200, body, link=link)

    monkeypatch.setattr(cs.requests, "get", get)
    tags = cs.Builder.get_docker_tag_records("ghcr.io/o/i")
    assert tags == [{"name": "1.0"}, {"name": "latest"}, {"name": "1.1-arm64"}]
    assert cs.select_last_version_tag(tags, "ghcr.io/o/i") == ("1.0", "1.0")
