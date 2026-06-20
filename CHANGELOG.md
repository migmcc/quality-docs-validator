# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial repository scaffold: packaging (`pyproject.toml`, Python 3.12+), `src/` layout,
  test/docs/examples structure, MIT license, CI stub.
- Project documentation: `docs/DECISIONS.md`, `docs/MVP_SCOPE.md`, `docs/ARCHITECTURE.md`,
  `docs/ROADMAP.md`.
- CLI entry points (`quality-docs-validator`, `qdv`) wired to a placeholder command.

### Notes
- The validation engine is **not implemented yet**. This release line covers scaffold only;
  the PFMEA ↔ Control Plan vertical slice lands in a subsequent build (see `docs/ROADMAP.md`).

<!--
## [0.1.0] - YYYY-MM-DD
First functional MVP: PFMEA ↔ Control Plan checker, ≥5 finding types, Markdown report,
terminal summary, bundled examples.
-->
