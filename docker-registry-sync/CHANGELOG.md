# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-02-27

- upgraded python to `3.11` from `3.8`
- using pydantic validation instead of jsonschema
- images are only synced when they are missing (using digest chess for this)
- all architectures are automatically copied over
- added `--use-explicit-tags` options which no longer syncs all the tags when the `tags: []` (left empty), this is an on or off option
- added support for including other `.yaml` files via the `!include file.yaml` directive


## [0.3.1] - 2025-02-21

- dregsy now syncs all image archtectures

## [0.3.0] - 2025-02-20

- upgraded dregsy to 0.5.1

## [0.2.1] - 2020-07-08
### Changed
- reduced parallel sync operations to 10 at a time to reduce third party system pressure

### Fixed
- debug mode no longer causes all syncs to fail

### Added
- missing skip-tls-verify in jsonschema
- coverage badge generation embedded locally in the project

## [0.2.0] - 2020-06-25
### Added
- started this changelog
- tox for test management with pytest
- debug mode to enable verbose debugging
- sync tasks are now executed in parallel
- `depends_on` and `id` fields to configuration used to guarantee order of execution
- test suite which covers most significant aspects of the code

### Changed
- documentation reflects new update
- output was cleaned up and simplified
- stable version moved to 0.2.0
- execution order changed to work on a dependency model

### Removed
- exit on first error no longer exists
- serial execution of tasks
- order of execution of stages is no longer the order in which stages are listed