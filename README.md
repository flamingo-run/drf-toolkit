![PyPI - Downloads](https://img.shields.io/pypi/dm/drf-toolkit)

![Github CI](https://github.com/flamingo-run/drf-toolkit/workflows/Github%20CI/badge.svg)
[![Maintainability](https://qlty.sh/badges/ba428e6a-df9e-450c-b395-d14295b36813/maintainability.svg)](https://qlty.sh/gh/flamingo-run/projects/drf-toolkit)
[![Code Coverage](https://qlty.sh/badges/ba428e6a-df9e-450c-b395-d14295b36813/test_coverage.svg)](https://qlty.sh/gh/flamingo-run/projects/drf-toolkit)

[![python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![python](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
# Django REST Framework Toolkit

A comprehensive toolkit that extends Django REST Framework with enhanced functionality and common patterns.

📚 **[Full Documentation](https://drf-kit.flamingo.codes)**

## Quick Start

### Requirements
- Python 3.11+
- Django 4.2+
- Django REST Framework 3.14+

### Installation

```bash
pip install drf-toolkit
```

For detailed usage instructions and examples, please visit our [Quick Start Guide](https://drf-kit.flamingo.codes/quick_start/).

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

## Development

### Setup

```bash
# Install dependencies
make dependencies

# Run tests
make test

# Format code
make style

# Serve documentation locally
make docs-serve
```

For more development commands, check the Makefile.

## Contributing

We welcome contributions! Please check our [Contributing Guide](https://drf-kit.flamingo.codes/contributing/) for guidelines.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
