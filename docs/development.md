# Development Setup

This guide will help you set up your development environment for contributing to DRF Toolkit.

## Prerequisites

- Python 3.9 or higher
- pip (Python package installer)
- Git

## Setting Up Your Development Environment

1. Clone the repository:
   ```bash
   git clone https://github.com/flamingo-run/drf-toolkit.git
   cd drf-toolkit
   ```

2. Create a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows use: .venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   make dependencies
   ```

## Running Tests

To run the test suite:

```bash
make test      # Run all checks including linting and unit tests
make unit      # Run only unit tests
```

## Code Style

We use [ruff](https://github.com/astral-sh/ruff) for code formatting and linting.

To check your code:
```bash
make lint      # Check code style
```

To automatically format your code:
```bash
make style     # Apply code style fixes
```

## Documentation

To build and serve the documentation locally:

```bash
mkdocs serve
```

Then visit http://127.0.0.1:8000 in your web browser.

## Making Changes

1. Create a new branch for your changes:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure all tests pass
3. Update documentation if necessary
4. Submit a pull request

For more detailed information about contributing, please see our [Contributing Guide](contributing.md).
