![Github CI](https://github.com/edukorg/drf-toolkit/workflows/Github%20CI/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/146215786039817ac8bc/maintainability)](https://codeclimate.com/github/edukorg/drf-toolkit/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/146215786039817ac8bc/test_coverage)](https://codeclimate.com/github/edukorg/drf-toolkit/test_coverage)
[![python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

# Django REST Framework Toolkit

A comprehensive toolkit that extends Django REST Framework with enhanced functionality and common patterns.

## Quick Start

### Requirements
- Python 3.11+
- Django 4.2+
- Django REST Framework 3.14+

### Installation

```bash
pip install drf-toolkit
```

## Features

DRF Toolkit provides a comprehensive set of tools and utilities for Django REST Framework:

- **Models**: Enhanced model functionality with diff tracking, soft delete, and more
- **Serializers**: Advanced serialization with automatic field handling
- **Views**: Extended viewsets with caching, filtering, and nested resources
- **Filters**: Powerful filtering capabilities with multiple filter types
- **Pagination**: Optimized pagination for better performance
- **Caching**: Flexible caching system with custom key generation
- **Signals**: Model operation tracking and signal management
- **Testing**: Comprehensive testing utilities for API endpoints

## Documentation

For detailed documentation, please visit our [documentation site](docs/). Here you'll find:

- Detailed guides for each feature
- API reference
- Best practices
- Examples and tutorials
- Development setup
- Contributing guidelines

## Development Setup

To set up the development environment:

1. Clone the repository:
```bash
git clone https://github.com/edukorg/drf-toolkit.git
cd drf-toolkit
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Install pre-commit hooks:
```bash
pre-commit install
```

5. Run tests:
```bash
pytest
```

### Code Quality

We use several tools to maintain code quality:

- **Black**: For code formatting
- **isort**: For import sorting
- **flake8**: For code style checking
- **mypy**: For type checking
- **pre-commit**: For running checks before commits

To run all quality checks:
```bash
tox
```

## Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

Please make sure to update tests as appropriate and follow the existing coding style.

## License

This project is licensed under the MIT License - see the LICENSE file for details.