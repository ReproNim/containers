"""Unit tests for create_singularities helper functions.

Run with::

    cd scripts
    pytest tests/test_create_singularities.py
"""
from __future__ import annotations

import importlib.machinery
import importlib.util
import sys
from pathlib import Path
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

# ---------------------------------------------------------------------------
# Load the script as a module (it has no .py extension)
# ---------------------------------------------------------------------------
_SCRIPT = Path(__file__).parent.parent / "create_singularities"
_loader = importlib.machinery.SourceFileLoader("create_singularities", str(_SCRIPT))
_spec = importlib.util.spec_from_loader("create_singularities", _loader)
assert _spec is not None
_mod = importlib.util.module_from_spec(_spec)
sys.modules.setdefault("create_singularities", _mod)
_loader.exec_module(_mod)

OCIRegistry = _mod.OCIRegistry
Builder = _mod.Builder


# ---------------------------------------------------------------------------
# OCIRegistry.for_image
# ---------------------------------------------------------------------------

class TestOCIRegistryForImage:
    def test_docker_hub_two_segment(self) -> None:
        reg, repo = OCIRegistry.for_image("nipreps/fmriprep")
        assert reg.host == "registry-1.docker.io"
        assert repo == "nipreps/fmriprep"

    def test_docker_hub_single_segment_becomes_library(self) -> None:
        reg, repo = OCIRegistry.for_image("ubuntu")
        assert reg.host == "registry-1.docker.io"
        assert repo == "library/ubuntu"

    def test_ghcr(self) -> None:
        reg, repo = OCIRegistry.for_image("ghcr.io/unfmontreal/skullduggery")
        assert reg.host == "ghcr.io"
        assert reg.auth_host == "ghcr.io"
        assert reg.service == "ghcr.io"
        assert repo == "unfmontreal/skullduggery"

    def test_quay(self) -> None:
        reg, repo = OCIRegistry.for_image("quay.io/biocontainers/samtools")
        assert reg.host == "quay.io"
        assert repo == "biocontainers/samtools"


# ---------------------------------------------------------------------------
# OCIRegistry.list_tags  (mocked HTTP)
# ---------------------------------------------------------------------------

def _make_response(json_data: Any) -> MagicMock:
    r = MagicMock()
    r.json.return_value = json_data
    r.raise_for_status.return_value = None
    return r


class TestOCIRegistryListTags:
    def test_ghcr_list_tags(self) -> None:
        token_resp = _make_response({"token": "tok123"})
        tags_resp = _make_response({"name": "unfmontreal/skullduggery", "tags": ["dev", "main"]})
        with patch.object(_mod, "retry_get", side_effect=[token_resp, tags_resp]) as mock_get:
            reg, repo = OCIRegistry.for_image("ghcr.io/unfmontreal/skullduggery")
            tags = reg.list_tags(repo)
        assert tags == ["dev", "main"]
        # check the auth header was forwarded
        tags_call_kwargs = mock_get.call_args.kwargs
        assert "headers" in tags_call_kwargs
        assert tags_call_kwargs["headers"]["Authorization"] == "Bearer tok123"

    def test_docker_hub_list_tags(self) -> None:
        token_resp = _make_response({"token": "dh_tok"})
        tags_resp = _make_response({"tags": ["25.2.5", "25.2.4", "latest"]})
        with patch.object(_mod, "retry_get", side_effect=[token_resp, tags_resp]):
            reg, repo = OCIRegistry.for_image("nipreps/fmriprep")
            tags = reg.list_tags(repo)
        assert "25.2.5" in tags


# ---------------------------------------------------------------------------
# Builder._select_best_version
# ---------------------------------------------------------------------------

class TestSelectBestVersion:
    def test_picks_highest_semver(self) -> None:
        result = Builder._select_best_version(
            ["0.1.0", "0.2.0", "1.0.1", "1.0.0"], "img"
        )
        assert result == ("1.0.1", "1.0.1")

    def test_skips_alpha_rc(self) -> None:
        result = Builder._select_best_version(
            ["1.0.0", "2.0.0a1", "1.5.0rc1"], "img"
        )
        assert result == ("1.0.0", "1.0.0")

    def test_no_semver_no_regex_returns_none(self) -> None:
        # Multiple non-semver tags without an explicit regex → None
        result = Builder._select_best_version(["dev", "main", "latest"], "img")
        assert result is None

    def test_no_semver_with_regex_returns_first_match(self) -> None:
        # version_regex was used to pre-filter; no semver found → fall back to tag verbatim
        result = Builder._select_best_version(
            ["main"], "img", version_regex=r"^main$"
        )
        assert result == ("main", "main")

    def test_only_good_versions_suppresses_non_semver_fallback(self) -> None:
        result = Builder._select_best_version(
            ["main"], "img", only_good_versions=True, version_regex=r"^main$"
        )
        assert result is None

    def test_single_tag_no_filter_returned_as_is(self) -> None:
        result = Builder._select_best_version(["latest"], "img")
        assert result == ("latest", "latest")

    def test_empty_list_returns_none(self) -> None:
        result = Builder._select_best_version([], "img")
        assert result is None

    def test_version_prefix_stripped(self) -> None:
        # "v1.2.3" → pure version is "1.2.3", tag stays "v1.2.3"
        result = Builder._select_best_version(["v1.2.3", "v1.1.0"], "img")
        assert result == ("1.2.3", "v1.2.3")


# ---------------------------------------------------------------------------
# Builder.get_last_version_tag  (unified OCI dispatcher, mocked HTTP)
# ---------------------------------------------------------------------------

class TestGetLastVersionTag:
    def _mock_registry(self, tags: list[str]) -> MagicMock:
        """Return a mock OCIRegistry whose list_tags always returns *tags*."""
        mock_reg = MagicMock()
        mock_reg.list_tags.return_value = tags
        return mock_reg

    def test_ghcr_semver(self) -> None:
        token_resp = _make_response({"token": "t"})
        tags_resp = _make_response({"tags": ["0.1.0", "0.2.0"]})
        with patch.object(_mod, "retry_get", side_effect=[token_resp, tags_resp]):
            result = Builder.get_last_version_tag("ghcr.io/org/img")
        assert result == ("0.2.0", "0.2.0")

    def test_ghcr_non_semver_with_regex(self) -> None:
        token_resp = _make_response({"token": "t"})
        tags_resp = _make_response({"tags": ["dev", "main"]})
        with patch.object(_mod, "retry_get", side_effect=[token_resp, tags_resp]):
            result = Builder.get_last_version_tag(
                "ghcr.io/unfmontreal/skullduggery", version_regex=r"^main$"
            )
        assert result == ("main", "main")

    def test_docker_hub(self) -> None:
        token_resp = _make_response({"token": "t"})
        tags_resp = _make_response({"tags": ["25.2.5", "25.2.4"]})
        with patch.object(_mod, "retry_get", side_effect=[token_resp, tags_resp]):
            result = Builder.get_last_version_tag("nipreps/fmriprep")
        assert result == ("25.2.5", "25.2.5")
