# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.1] - 2025-11-05

### Fixed

- Fixed catalog validation errors when `documentation_url` field contains empty strings
- Updated catalog generation to use `null` instead of empty strings for missing documentation URLs
- Fixed datetime comparison issue between timezone-aware and timezone-naive datetimes in catalog updates
- Updated default remote URL to point to correct repository
- Catalog update command now works properly without validation errors

### Changed

- Improved error handling in catalog update process
- Enhanced timezone handling for datetime comparisons

## [1.0.0] - 2024-01-01

### Added

- Initial release of Amazon Q Rule Manager
- Global and workspace rule management
- Rule catalog with comprehensive metadata
- CLI interface with rich formatting
- Support for multiple rule categories (AWS, Python, Terraform, etc.)
- Remote catalog synchronization
- Rule installation and management system
