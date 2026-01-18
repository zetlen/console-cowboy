# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.4.0](https://github.com/zetlen/console-cowboy/compare/v0.3.0...v0.4.0) (2026-01-18)


### Features

* **ghostty:** add Ghostty 1.2.0 quick-terminal features and font-feature support ([#48](https://github.com/zetlen/console-cowboy/issues/48)) ([ac0b0eb](https://github.com/zetlen/console-cowboy/commit/ac0b0eb72cc09dec14108ee13b8f1316dba4b6e2))
* **schema:** add environment_variables and shell_args to BehaviorConfig ([#47](https://github.com/zetlen/console-cowboy/issues/47)) ([95ca34a](https://github.com/zetlen/console-cowboy/commit/95ca34a45a3dff981ff3d3bd843eb2beaddd2036))


### Bug Fixes

* **alacritty:** support modern [terminal.shell] config location ([#45](https://github.com/zetlen/console-cowboy/issues/45)) ([80dd339](https://github.com/zetlen/console-cowboy/commit/80dd339b9f642fc0e5caad2a4a72815aa99deb2e)), closes [#43](https://github.com/zetlen/console-cowboy/issues/43)
* **ci:** switch to MishaKav/pytest-coverage-comment action ([#46](https://github.com/zetlen/console-cowboy/issues/46)) ([1386828](https://github.com/zetlen/console-cowboy/commit/13868288331160dd42affdedc8b3717702b0673b))
* **kitty:** add power user config support for critical settings ([#49](https://github.com/zetlen/console-cowboy/issues/49)) ([ab5d4cb](https://github.com/zetlen/console-cowboy/commit/ab5d4cb9b6d731561e85616cf09c334faa20b231))


### Code Refactoring

* **terminals:** extract common patterns into mixins ([#37](https://github.com/zetlen/console-cowboy/issues/37)) ([6f84e45](https://github.com/zetlen/console-cowboy/commit/6f84e452af7d93ad8e5963b1f54224647f3d83a4))


### Miscellaneous

* fix hallucinated coverage action commit ([#38](https://github.com/zetlen/console-cowboy/issues/38)) ([81a806f](https://github.com/zetlen/console-cowboy/commit/81a806f621ad74e8fde20890424b528168b37e84))

## [0.3.0](https://github.com/zetlen/console-cowboy/compare/v0.2.0...v0.3.0) (2026-01-17)


### Features

* add knowledge base builder and /docs command ([#33](https://github.com/zetlen/console-cowboy/issues/33)) ([d723a7e](https://github.com/zetlen/console-cowboy/commit/d723a7ed7358618a9562dd038e32088dcac84b37))
* **cli:** redesign CLI with unified --from/--to interface ([#30](https://github.com/zetlen/console-cowboy/issues/30)) ([af74ee1](https://github.com/zetlen/console-cowboy/commit/af74ee1f2d4e0edd24e23193ab9fb94aa5eceec0))
* **keybindings:** add comprehensive keybinding support across terminals ([#32](https://github.com/zetlen/console-cowboy/issues/32)) ([93f4613](https://github.com/zetlen/console-cowboy/commit/93f4613564514f93960f89adcb0dfcb911c8c936)), closes [#18](https://github.com/zetlen/console-cowboy/issues/18)
* **schema:** add TabConfig and PaneConfig for cross-terminal tab/pane settings ([#36](https://github.com/zetlen/console-cowboy/issues/36)) ([a4fce12](https://github.com/zetlen/console-cowboy/commit/a4fce12b224003d7baab7f9ed1c7c8455de49012))
* **wezterm:** replace regex parsing with Lua interpreter ([#34](https://github.com/zetlen/console-cowboy/issues/34)) ([13fdb3b](https://github.com/zetlen/console-cowboy/commit/13fdb3bf84b6ed0fac6eb4b011d31d3b2b46d590))

## [0.2.0](https://github.com/zetlen/console-cowboy/compare/v0.1.2...v0.2.0) (2026-01-17)


### Features

* **ctec:** add TextHintConfig for regex-based text pattern detection ([#29](https://github.com/zetlen/console-cowboy/issues/29)) ([270ec3f](https://github.com/zetlen/console-cowboy/commit/270ec3fba1be5687dd1910e978a6ca04fca7b44a))


### Bug Fixes

* add manual trigger for publishing to release-please workflow ([#25](https://github.com/zetlen/console-cowboy/issues/25)) ([600d10a](https://github.com/zetlen/console-cowboy/commit/600d10ab9359e53d4bfbc4fa87bbbcd3051dd5d4))
* allow manual trigger for publish workflow ([#23](https://github.com/zetlen/console-cowboy/issues/23)) ([21d6188](https://github.com/zetlen/console-cowboy/commit/21d6188b35cdf3ecbd8889659955c7aa25ce9efc))
* **iterm2:** improve hotkey window and window type parsing ([#28](https://github.com/zetlen/console-cowboy/issues/28)) ([618160e](https://github.com/zetlen/console-cowboy/commit/618160e0ef90a2308495425dba3a2ed658bacded))


### Miscellaneous

* add gemini config ([#26](https://github.com/zetlen/console-cowboy/issues/26)) ([2cd6f53](https://github.com/zetlen/console-cowboy/commit/2cd6f53fedded64df5cc5930bbe484e45aa4b572))

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
