# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.2](https://github.com/zetlen/console-cowboy/compare/v0.1.1...v0.1.2) (2026-01-17)


### Bug Fixes

* inline publish job to fix PyPI trusted publishing ([#15](https://github.com/zetlen/console-cowboy/issues/15)) ([9a073d0](https://github.com/zetlen/console-cowboy/commit/9a073d005c888b3a981d3514746625d106945f86))

## [0.1.1](https://github.com/zetlen/console-cowboy/compare/v0.1.0...v0.1.1) (2026-01-17)


### Bug Fixes

* undamage release process ([#13](https://github.com/zetlen/console-cowboy/issues/13)) ([7950e7e](https://github.com/zetlen/console-cowboy/commit/7950e7e5b66a999415213404787cfce571cce8e0))


### Documentation

* update README and fix CI workflows ([#12](https://github.com/zetlen/console-cowboy/issues/12)) ([c45f80b](https://github.com/zetlen/console-cowboy/commit/c45f80b031b4ddd0f43a435517f74d9bcc10c9cf))


### Continuous Integration

* add release-please for automated releases ([#11](https://github.com/zetlen/console-cowboy/issues/11)) ([4d9776b](https://github.com/zetlen/console-cowboy/commit/4d9776bbe63c1da94904a0753357c11fc871d4a3))

## [0.1.0](https://github.com/zetlen/console-cowboy/releases/tag/v0.1.0) (Initial Release)

### Features

- Terminal adapter plugin system with CTEC intermediate representation
- Support for Ghostty, iTerm2, Alacritty, Kitty, and WezTerm
- Support for macOS Terminal.app
- Support for VSCode integrated terminal
- CLI commands: `export`, `import`, `convert`, `list`, `info`
- TOML, JSON, and YAML serialization formats
- Color normalization utilities
- Round-trip conversion preserving terminal-specific settings
