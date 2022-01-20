# Quick Start Guide

This guide will help you get started with DRF Toolkit quickly. We'll cover installation, basic setup, and common use cases.

## Installation

```bash
pip install drf-toolkit
```

## Basic Setup

1. Add `drf_kit` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    'drf_kit',
]
```

2. Configure your Django REST Framework settings (if not already done):

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'drf_kit.pagination.PageNumberPagination',
    'PAGE_SIZE': 100,
}
```

## Common Use Cases

### 1. Enhanced Models

Use our enhanced model classes for common functionality:

```python
from drf_kit.models import BaseModel

class User(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
```

### 2. Advanced Filtering

Implement powerful filtering in your views:

```python
from drf_kit.filters import FilterSet

class UserFilter(FilterSet):
    class Meta:
        model = User
        fields = ['name', 'email']

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    filterset_class = UserFilter
```

### 3. Soft Delete

Add soft delete capability to your models:

```python
from drf_kit.models import SoftDeleteModel

class Document(SoftDeleteModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
```

### 4. Enhanced Serializers

Use our enhanced serializers for better validation and flexibility:

```python
from drf_kit.serializers import ModelSerializer

class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'name', 'email']
```

## Next Steps

- Check out the [Models](models.md) documentation for more model features
- Learn about [Serializers](serializers.md) for advanced serialization
- Explore [Views](views.md) for enhanced viewset capabilities
- See [Filters](filters.md) for advanced filtering options
- Review [Testing](testing.md) for testing utilities

For more detailed information about specific features, check the respective documentation sections.