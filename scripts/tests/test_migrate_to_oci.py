#!/usr/bin/env python3
"""
Unit tests for scripts/migrate_to_oci migration script.

These tests validate the helper functions and logic in the migration script
by importing it as a Python module after creating a temporary .py symlink.
"""

from __future__ import annotations
from pathlib import Path
from textwrap import dedent
import json
import pytest
import subprocess
import tempfile
import importlib.util
import sys

# Create a temporary .py file that imports from the script
# This is needed because importlib needs a .py extension
script_path = (Path(__file__).parent.parent / "migrate_to_oci").resolve()
temp_py_path = script_path.parent / "migrate_to_oci_temp.py"

# Read the script content and write it to a temp .py file for testing
if not temp_py_path.exists():
    import shutil
    shutil.copy(script_path, temp_py_path)

# Import from the temp file
spec = importlib.util.spec_from_file_location("migrate_to_oci", str(temp_py_path))
if spec is None or spec.loader is None:
    raise ImportError(f"Could not load module from {temp_py_path}")
migrate_module = importlib.util.module_from_spec(spec)
sys.modules["migrate_to_oci"] = migrate_module
spec.loader.exec_module(migrate_module)

OCIMigrator = migrate_module.OCIMigrator
MigrationResult = migrate_module.MigrationResult


@pytest.mark.ai_generated
class TestSingularityFileParsing:
    """Test parsing of Singularity recipe files."""

    def test_parse_automagic_file(self, tmp_path: Path) -> None:
        """Test parsing a standard auto-generated Singularity file."""
        singfile = tmp_path / "Singularity.test"
        singfile.write_text(dedent("""
            #
            # Automagically prepared for ReproNim/containers distribution.
            # See http://github.com/ReproNim/containers for more info
            #
            Bootstrap: docker
            From: bids/validator:1.2.3

            %post
            mkdir -p /data
        """))

        migrator = OCIMigrator(
            repo_dir=tmp_path,
            images_dir=tmp_path / "images",
            images_oci_dir=tmp_path / "images-oci",
        )

        result = migrator.parse_singularity_file(singfile)

        assert result is not None
        assert result["namespace"] == "bids"
        assert result["image"] == "validator"
        assert result["tag"] == "1.2.3"
        assert result["docker_url"] == "bids/validator:1.2.3"

    def test_parse_non_automagic_file(self, tmp_path: Path) -> None:
        """Test that non-auto-generated files are skipped."""
        singfile = tmp_path / "Singularity.custom"
        singfile.write_text(dedent("""
            Bootstrap: docker
            From: custom/image:1.0

            %post
            echo "Custom setup"
        """))

        migrator = OCIMigrator(
            repo_dir=tmp_path,
            images_dir=tmp_path / "images",
            images_oci_dir=tmp_path / "images-oci",
        )

        result = migrator.parse_singularity_file(singfile)
        assert result is None

    def test_parse_file_with_complex_namespace(self, tmp_path: Path) -> None:
        """Test parsing file with registry/namespace/image format."""
        singfile = tmp_path / "Singularity.test"
        singfile.write_text(dedent("""
            #
            # Automagically prepared for ReproNim/containers distribution.
            #
            Bootstrap: docker
            From: nipreps/fmriprep:20.2.0

            %post
            mkdir -p /data
        """))

        migrator = OCIMigrator(
            repo_dir=tmp_path,
            images_dir=tmp_path / "images",
            images_oci_dir=tmp_path / "images-oci",
        )

        result = migrator.parse_singularity_file(singfile)

        assert result is not None
        assert result["namespace"] == "nipreps"
        assert result["image"] == "fmriprep"
        assert result["tag"] == "20.2.0"

    def test_parse_file_missing_from_line(self, tmp_path: Path) -> None:
        """Test that files without From: line return None."""
        singfile = tmp_path / "Singularity.broken"
        singfile.write_text(dedent("""
            #
            # Automagically prepared for ReproNim/containers distribution.
            #
            Bootstrap: docker

            %post
            mkdir -p /data
        """))

        migrator = OCIMigrator(
            repo_dir=tmp_path,
            images_dir=tmp_path / "images",
            images_oci_dir=tmp_path / "images-oci",
        )

        result = migrator.parse_singularity_file(singfile)
        assert result is None


@pytest.mark.ai_generated
class TestImageNaming:
    """Test OCI and SIF image name generation."""

    def test_get_oci_image_name(self, tmp_path: Path) -> None:
        """Test OCI image name generation from Singularity file path."""
        migrator = OCIMigrator(
            repo_dir=tmp_path,
            images_dir=tmp_path / "images",
            images_oci_dir=tmp_path / "images-oci",
        )

        singfile = tmp_path / "images" / "bids" / "Singularity.bids-validator--1.2.3"
        singfile.parent.mkdir(parents=True, exist_ok=True)

        oci_name = migrator.get_oci_image_name(singfile)
        assert oci_name == "bids/bids-validator--1.2.3.oci"

    def test_get_sif_image_name(self, tmp_path: Path) -> None:
        """Test SIF image name generation from Singularity file path."""
        migrator = OCIMigrator(
            repo_dir=tmp_path,
            images_dir=tmp_path / "images",
            images_oci_dir=tmp_path / "images-oci",
        )

        singfile = tmp_path / "images" / "bids" / "Singularity.bids-validator--1.2.3"
        singfile.parent.mkdir(parents=True, exist_ok=True)

        sif_name = migrator.get_sif_image_name(singfile)
        assert sif_name == "bids/bids-validator--1.2.3.sif"

    def test_get_oci_image_name_different_family(self, tmp_path: Path) -> None:
        """Test OCI image name with different family directory."""
        migrator = OCIMigrator(
            repo_dir=tmp_path,
            images_dir=tmp_path / "images",
            images_oci_dir=tmp_path / "images-oci",
        )

        singfile = tmp_path / "images" / "neurodesk" / "Singularity.neurodesk-afni--21.2.00"
        singfile.parent.mkdir(parents=True, exist_ok=True)

        oci_name = migrator.get_oci_image_name(singfile)
        assert oci_name == "neurodesk/neurodesk-afni--21.2.00.oci"


@pytest.mark.ai_generated
class TestAnnexVerification:
    """Test git-annex URL verification."""

    def test_verify_annex_urls_no_git_repo(self, tmp_path: Path) -> None:
        """Test verification fails gracefully when not in a git repo."""
        migrator = OCIMigrator(
            repo_dir=tmp_path,
            images_dir=tmp_path / "images",
            images_oci_dir=tmp_path / "images-oci",
        )

        # Should return False when git commands fail
        result = migrator.verify_annex_urls(tmp_path / "nonexistent")
        assert result is False


@pytest.mark.ai_generated
class TestMigrationResult:
    """Test MigrationResult dataclass."""

    def test_migration_result_success(self, tmp_path: Path) -> None:
        """Test creating a successful migration result."""
        singfile = tmp_path / "test.sing"
        result = MigrationResult(
            singularity_file=singfile,
            success=True,
            oci_image_path=tmp_path / "test.oci",
            sif_image_path=tmp_path / "test.sif",
        )

        assert result.success is True
        assert result.error_message is None
        assert result.singularity_file == singfile

    def test_migration_result_failure(self, tmp_path: Path) -> None:
        """Test creating a failed migration result."""
        singfile = tmp_path / "test.sing"
        result = MigrationResult(
            singularity_file=singfile,
            success=False,
            error_message="Test error",
        )

        assert result.success is False
        assert result.error_message == "Test error"
        assert result.oci_image_path is None


@pytest.mark.ai_generated
def test_migrator_initialization(tmp_path: Path) -> None:
    """Test OCIMigrator initialization."""
    images_dir = tmp_path / "images"
    images_oci_dir = tmp_path / "images-oci"

    migrator = OCIMigrator(
        repo_dir=tmp_path,
        images_dir=images_dir,
        images_oci_dir=images_oci_dir,
        skip_failures=True,
    )

    assert migrator.repo_dir == tmp_path
    assert migrator.images_dir == images_dir
    assert migrator.images_oci_dir == images_oci_dir
    assert migrator.skip_failures is True
    assert migrator.results == []
