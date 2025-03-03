# Django REST Framework Toolkit

![Github CI](https://github.com/flamingo-run/drf-toolkit/workflows/Github%20CI/badge.svg)
[![Maintainability](https://api.codeclimate.com/v1/badges/146215786039817ac8bc/maintainability)](https://codeclimate.com/github/flamingo-run/drf-toolkit/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/146215786039817ac8bc/test_coverage)](https://codeclimate.com/github/flamingo-run/drf-toolkit/test_coverage)
[![python](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![python](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)

A comprehensive toolkit that extends Django REST Framework with enhanced functionality and common patterns.

## Overview

[Django](https://www.djangoproject.com/) and [DRF](https://www.django-rest-framework.org/) provide an awesome combination for building REST APIs.

DRF supports many great [plugins](https://www.django-rest-framework.org/community/third-party-packages/) that extend its capabilities even further.

The DRF Toolkit applies common [RESTFul patterns](https://restfulapi.net/) to the framework by adding base classes that can be used in your existing DRF projects.

Most use cases are covered by DRF Toolkit, allowing your project to be simpler so you can focus on the business logic.

## Motivation

While Django REST Framework provides excellent foundations for building APIs, developers often find themselves reimplementing common patterns or searching for multiple packages to fill functionality gaps. DRF Toolkit addresses these challenges by:

- **Comprehensive Feature Set**: Providing a unified solution for common API requirements like soft deletion, diff tracking, advanced filtering, and nested resources, eliminating the need for multiple third-party packages.

- **Enhanced Extensibility**: Offering base classes and mixins that seamlessly integrate with DRF, making it easy to extend and customize functionality while maintaining clean, maintainable code.

- **Production-Ready Features**: Including optimized solutions for caching, pagination, and database operations that are battle-tested and performance-focused.

- **Developer Experience**: Reducing boilerplate code and providing intuitive abstractions that make it easier to implement complex API patterns while following REST best practices.

- **Missing DRF Features**: Filling gaps in DRF's core functionality with features like automatic field handling, enhanced model tracking, and comprehensive testing utilities.

## Features

DRF Toolkit provides a comprehensive set of tools and utilities for Django REST Framework:

- [**Models**](models/index.md): Enhanced model functionality with diff tracking, soft delete, and more
- [**Serializers**](serializers.md): Advanced serialization with automatic field handling
- [**Views**](views.md): Extended viewsets with caching, filtering, and nested resources
- [**Filters**](filters.md): Powerful filtering capabilities with multiple filter types
- [**Pagination**](pagination.md): Optimized pagination for better performance
- [**Caching**](caching.md): Flexible caching system with custom key generation
- [**Signals**](signals.md): Model operation tracking and signal management
- [**Testing**](testing.md): Comprehensive testing utilities for API endpoints

Additional features include:
- [**Fields**](fields.md): Custom model and serializer fields
- [**Storage**](storage.md): Enhanced file storage capabilities

Check out our detailed documentation sections to learn more about each feature.
