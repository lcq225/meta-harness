# Changelog

All notable changes will be documented in this file.

## [1.0.0] - 2026-04-01

### Added
- Initial release
- **HarnessEvaluator**: Multi-dimensional output quality evaluation
  - Correctness (30%)
  - Completeness (20%)
  - Efficiency (15%)
  - Maintainability (15%)
  - Security (10%)
  - Test Coverage (10%)
- **ExperienceTracker**: SQLite-based experience storage
  - Record and search experiences
  - Statistics and analytics
  - Tool effectiveness analysis
  - Data export (JSON)
  - Auto archive and cleanup
- **CoPaw Integration**: Integration module for CoPaw framework
- **Tests**: 23 test cases with 100% pass rate
- **Documentation**: 
  - README (English/中文)
  - Integration guide
  - Contributing guide

### Dependencies
- Python >= 3.10
- SQLAlchemy >= 2.0

---

For older versions, see [release tags](https://github.com/lcq225/meta-harness/tags).

## Upgrade Notes

### From 0.x to 1.0.0
This is the first stable release. No migration needed.

---

*This changelog follows [Keep a Changelog](https://keepachangelog.com/) guidelines.*