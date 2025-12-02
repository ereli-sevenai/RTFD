# Contributing to RTFD

Thank you for your interest in contributing to RTFD! This document outlines how to contribute code and how the release process works.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/aserper/RTFD.git
   cd RTFD
   ```

2. Install in development mode:
   ```bash
   pip install -e .
   # or with uv:
   uv pip install -e .
   ```

3. Run tests:
   ```bash
   pytest
   ```

## Making Changes

1. Create a feature branch:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and commit with clear messages:
   ```bash
   git commit -m "feat: add new feature"
   # or
   git commit -m "fix: resolve issue with X"
   ```

3. Push and create a pull request on GitHub

## Code Quality

- Follow PEP 8 style guidelines
- Write clear commit messages
- Include docstrings for public functions
- Add tests for new features
- Ensure all tests pass before submitting PR

## Questions?

Feel free to open an issue or discussion if you have questions about the contribution process!
