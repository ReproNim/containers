# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Build/Test Commands
- Run all tests: `bats -t scripts/tests`
- Run a single test: `bats -t scripts/tests/test_singularity_cmd.bats`
- Lint shell scripts: `shellcheck scripts/*`

## Code Style Guidelines
- Follow DataLad/Git-Annex conventions for repository structure
- Shell scripts should pass shellcheck validation
- Maintain YODA principles (store all dependencies within the dataset)
- Tests use the bats framework with helpers in `scripts/tests/test_helpers.bash`
- Use snake_case for function and variable names
- Scripts should include proper error handling and validate inputs
- Document environment variables that affect script behavior
- Maintain backward compatibility with DataLad commands
- Follow proper Singularity image naming: `name--version.sing` format
