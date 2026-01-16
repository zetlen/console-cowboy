# console-cowboy

[![PyPI](https://img.shields.io/pypi/v/console-cowboy.svg)](https://pypi.org/project/console-cowboy/)
[![Changelog](https://img.shields.io/github/v/release/zetlen/console-cowboy?include_prereleases&label=changelog)](https://github.com/zetlen/console-cowboy/releases)
[![Tests](https://github.com/zetlen/console-cowboy/actions/workflows/test.yml/badge.svg)](https://github.com/zetlen/console-cowboy/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/zetlen/console-cowboy/blob/master/LICENSE)

Hop terminals like you hop linux distributions.

## Installation

Install this tool using `pip`:
```bash
pip install console-cowboy
```
## Usage

For help, run:
```bash
console-cowboy --help
```
You can also use:
```bash
python -m console_cowboy --help
```
## Development

To contribute to this tool, first checkout the code. Then create a new virtual environment:
```bash
cd console-cowboy
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
pip install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
