# Contributing to Meta-Harness

Thank you for your interest in contributing!

## Ways to Contribute

1. **Report Bugs** - Create an issue with clear steps to reproduce
2. **Suggest Features** - Open an issue with detailed description
3. **Submit PRs** - Fix bugs, add features, improve documentation
4. **Improve Tests** - Add test cases for better coverage

## Development Setup

```bash
# Clone repository
git clone https://github.com/lcq225/meta-harness.git
cd meta-harness

# Install in development mode
pip install -e ".[dev]"

# Run tests
pytest tests/
```

## Code Style

- Follow PEP 8
- Use Black for formatting: `black src/ tests/`
- Use Ruff for linting: `ruff check src/ tests/`
- Type hints are required for new code

## Pull Request Process

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests if applicable
5. Run the test suite
6. Commit with clear messages
7. Push to your fork
8. Submit a Pull Request

## Commit Messages

Use conventional commits:

```
feat: add new feature
fix: resolve bug
docs: update documentation
test: add tests
refactor: code refactoring
chore: maintenance
```

## Issue Guidelines

- Search existing issues before creating new ones
- Use clear titles
- Provide reproduction steps for bugs
- Include environment details (Python version, OS, etc.)

## Code of Conduct

- Be respectful and inclusive
- Welcome newcomers
- Accept constructive criticism gracefully

---

⭐ Thank you for contributing!