# OCI-Based Container Workflow Migration Guide

This guide documents the implementation of the OCI-based container workflow as described in [use-oci-1.md](use-oci-1.md).

## Overview

The new workflow migrates from building Singularity containers directly from Docker images to using OCI containers as an intermediate step. This provides better reproducibility and URL-based availability for all container components.

## Components

### 1. `scripts/oci_cmd`

A simple wrapper script that passes commands to `apptainer`. This script is registered with DataLad containers as the command wrapper for OCI containers.

**Usage:**
```bash
scripts/oci_cmd <apptainer-command> [arguments...]
```

**Example:**
```bash
scripts/oci_cmd run container.oci/
scripts/oci_cmd build output.sif input.oci/
```

### 2. `scripts/migrate_to_oci`

Migration script that converts existing auto-generated Singularity containers to the OCI-based workflow.

**Features:**
- Identifies auto-generated Singularity files (marked with "Automagically prepared")
- Creates OCI images in `images-oci/` subdataset
- Builds SIF files from OCI images
- Updates `.datalad/config` to point to new SIF files
- Removes old Singularity recipe and `.sing` files
- Verifies all annex files are available from URLs

**Usage:**
```bash
# Migrate all auto-generated containers
scripts/migrate_to_oci

# Migrate specific containers
scripts/migrate_to_oci images/bids/Singularity.bids-validator--1.2.3

# Continue even if some migrations fail
scripts/migrate_to_oci --skip-failures

# Log failures to a file
scripts/migrate_to_oci --log-file migration_failures.log
```

## Workflow

### Creating New OCI-Based Containers

1. **Add OCI container** (in `images-oci/` subdataset):
   ```bash
   cd images-oci/
   datalad containers-add \
     --url oci:docker://bids/validator:1.2.3 \
     -i bids/bids-validator--1.2.3.oci \
     bids-validator
   ```

2. **Verify annex URLs**:
   ```bash
   git annex find --not --in datalad --and --not --in web bids/bids-validator--1.2.3.oci
   ```
   This should return empty output (all files have URLs).

3. **Build SIF image** (from repository root):
   ```bash
   datalad run \
     -m "Build SIF image for bids/bids-validator--1.2.3.sif" \
     --output images/bids/bids-validator--1.2.3.sif \
     scripts/oci_cmd build \
       images/bids/bids-validator--1.2.3.sif \
       images-oci/bids/bids-validator--1.2.3.oci/
   ```

4. **Register container** (if needed):
   ```bash
   datalad containers-add \
     bids-validator \
     -i images/bids/bids-validator--1.2.3.sif \
     --update \
     --call-fmt "{img_dspath}/scripts/singularity_cmd run {img} {cmd}"
   ```

### Migrating Existing Containers

The migration process for a single container involves:

1. **Parse Singularity file** - Extract Docker image URL from `From:` line
2. **Create OCI image** - Use `datalad containers-add` with `oci:docker://` URL
3. **Verify URLs** - Ensure all annex files are available from web
4. **Build SIF** - Convert OCI to SIF using `scripts/oci_cmd build`
5. **Update config** - Point `.datalad/config` to new SIF file
6. **Remove old files** - Delete Singularity recipe and `.sing` file
7. **Commit changes** - Create a commit documenting the migration

**Example migration workflow:**
```bash
# Test on simple cases first
scripts/migrate_to_oci \
  images/bids/Singularity.bids-validator--1.2.3 \
  images/bids/Singularity.bids-rshrf--1.0.0

# If successful, migrate all
scripts/migrate_to_oci --skip-failures --log-file migration.log
```

## Repository Structure

```
.
├── images/                    # SIF files (final container images)
│   ├── bids/
│   │   ├── bids-validator--1.2.3.sif
│   │   └── bids-aa--0.2.0.sif
│   └── neurodesk/
│       └── neurodesk-afni--21.2.00.sif
│
├── images-oci/               # OCI containers (subdataset)
│   ├── bids/
│   │   ├── bids-validator--1.2.3.oci/
│   │   └── bids-aa--0.2.0.oci/
│   └── neurodesk/
│       └── neurodesk-afni--21.2.00.oci/
│
├── scripts/
│   ├── oci_cmd              # Apptainer wrapper
│   ├── migrate_to_oci       # Migration script
│   └── singularity_cmd      # Existing Singularity wrapper
│
└── .datalad/
    └── config               # Container registrations
```

## Verification

After migration, verify that:

1. **All annex files have URLs:**
   ```bash
   git annex find --not --in datalad --and --not --in web images-oci/
   ```
   Should return empty.

2. **SIF files exist:**
   ```bash
   ls -lh images/bids/*.sif
   ```

3. **Container configuration updated:**
   ```bash
   git config -f .datalad/config --get-regexp 'datalad.containers.*.image' | grep '.sif$'
   ```

4. **Old files removed:**
   ```bash
   git log --all -- 'images/*/Singularity.*' | head -20
   ```

## Testing

### Unit Tests

**BATS tests for `oci_cmd`:**
```bash
bats -t scripts/tests/test_oci_cmd.bats
```

**Python tests for migration script:**
```bash
python -m pytest scripts/tests/test_migrate_to_oci.py -v
```

### Integration Testing

Test the full workflow on a simple container:

```bash
# Create test OCI container
cd images-oci/
datalad containers-add \
  --url oci:docker://alpine:latest \
  -i test/test-alpine.oci \
  test-alpine

# Verify URLs
git annex find --not --in datalad --and --not --in web test/test-alpine.oci

# Build SIF
cd ..
datalad run \
  -m "Build test SIF" \
  --output images/test/test-alpine.sif \
  scripts/oci_cmd build images/test/test-alpine.sif images-oci/test/test-alpine.oci/

# Test container
scripts/oci_cmd exec images-oci/test/test-alpine.oci/ echo "Hello from OCI"
scripts/singularity_cmd exec images/test/test-alpine.sif echo "Hello from SIF"
```

## Troubleshooting

### OCI container creation fails

**Issue:** `datalad containers-add` fails with OCI URL

**Solution:** Ensure you have:
- DataLad container extension with OCI support
- Skopeo installed
- Network access to Docker Hub

### Annex files without URLs

**Issue:** `git annex find --not --in datalad --and --not --in web` returns files

**Solution:**
```bash
# For each file, register the URL manually
git annex registerurl <key> <url>
```

### SIF build fails

**Issue:** `scripts/oci_cmd build` fails

**Solution:**
- Ensure apptainer/singularity is installed
- Check disk space (SIF files can be large)
- Verify OCI directory exists and is valid

### Migration script fails mid-process

**Issue:** Script fails partway through migration

**Solution:**
- Use `--skip-failures` flag to continue past failures
- Check `--log-file` output for specific errors
- Manually fix failed migrations and re-run

## Benefits of OCI-Based Workflow

1. **URL Availability** - All container components are available via URLs (no special remotes needed)
2. **Reproducibility** - OCI format is standardized and widely supported
3. **Flexibility** - Can use either OCI or SIF format depending on needs
4. **Better Tracking** - DataLad tracks all steps of container creation
5. **Easier Maintenance** - Updates only need to touch OCI layer, SIF can be rebuilt

## Future Enhancements

1. **Automated Updates** - Script to check for updated Docker images and rebuild
2. **Parallel Migration** - Process multiple containers concurrently
3. **Rollback Support** - Ability to revert failed migrations
4. **CI/CD Integration** - Automated testing of migrated containers
5. **Cache Management** - Tools to manage OCI cache and temporary files

## References

- [Original Design Document](use-oci-1.md)
- [DataLad Container Documentation](https://docs.datalad.org/projects/container/)
- [Apptainer Documentation](https://apptainer.org/docs/)
- [OCI Specification](https://github.com/opencontainers/image-spec)
