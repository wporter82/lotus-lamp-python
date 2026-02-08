# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2026-02-08

### Added
- Time/Scheduling support
- Example script

### Fixed
- Removed unicode characters in config creation
- Updated documentation with timer protocol

## [1.0.1] - 2026-02-06

### Fixed
- Fixed documentation links in README.md - now point to GitHub instead of relative paths (fixes 404 errors on PyPI)
- Fixed LICENSE link in README.md to point to GitHub
- Fixed package name format from `lotus-lamp` to `lotus_lamp` to comply with PyPI naming requirements (Note: users can still install using either `pip install lotus-lamp` or `pip install lotus_lamp`)

## [1.0.0] - 2026-02-06

### Added
- Initial release
- Complete BLE protocol implementation for Lotus Lamp devices
- Support for 213 built-in animation modes with official names
- RGB color control (16.7 million colors)
- Brightness control (0-100%)
- Speed control (0-100%)
- Power on/off control
- Mode search and lookup functionality
- Category-based mode organization (8 categories)
- Auto UUID discovery for different lamp models
- Interactive setup wizard
- Multi-device support
- Configuration management system
- 5 example scripts (browser, animation, discovery, multi-device)
- Comprehensive documentation (README, CONFIGURATION, TESTING, PROTOCOL, MODES)
- Test suite with 94 tests

### Documentation
- Complete BLE protocol documentation
- All 213 modes documented with categories
- Configuration guide for advanced usage
- Testing guide
- Interactive mode browser example

[1.1.0]: https://github.com/wporter82/lotus-lamp-python/compare/v1.0.1...v1.1.0
[1.0.1]: https://github.com/wporter82/lotus-lamp-python/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/wporter82/lotus-lamp-python/releases/tag/v1.0.0
