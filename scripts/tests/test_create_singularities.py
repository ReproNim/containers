"""Tests for the helpers of scripts/create_singularities

Run with `nox -e test` under scripts/ .
"""
from importlib.machinery import SourceFileLoader
from importlib.util import module_from_spec, spec_from_loader
from pathlib import Path
import sys
from typing import Any, Optional

import pytest

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
