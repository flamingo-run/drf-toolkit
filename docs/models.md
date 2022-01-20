# Models

DRF Toolkit provides a rich set of model types and mixins to enhance Django's model functionality. Each model type is designed to handle specific use cases while maintaining clean and organized code.

## Available Models

### Base Models
- [Base Models](models/base.md) - Core functionality including timestamps and change tracking
- [Diff Models](models/diff.md) - Track changes to model fields

### Feature Models
- [Availability Models](models/availability.md) - Time-based availability management
- [File Models](models/file.md) - Enhanced file handling capabilities
- [Inheritance Models](models/inheritance.md) - Advanced model inheritance support
- [Ordered Models](models/ordered.md) - Automatic sequence management
- [Soft Delete Models](models/soft_delete.md) - Soft deletion functionality

### Combined Models
See [Model Combinations](models/combinations.md) for pre-built combinations and custom combination guidelines.

## Quick Start

Most models should inherit from BaseModel or one of its variants:

```python
from drf_kit.models import BaseModel

class SimpleModel(BaseModel):
    name = models.CharField(max_length=100)
    # Automatically includes:
    # - created_at
    # - updated_at
    # - change tracking
    # - file handling
```

For more complex needs, use feature-specific models:

```python
from drf_kit.models import (
    SoftDeleteModel,
    AvailabilityModel,
    OrderedModel
)

# Soft deletion support
class Document(SoftDeleteModel):
    title = models.CharField(max_length=100)

# Time-based availability
class Event(AvailabilityModel):
    name = models.CharField(max_length=100)

# Automatic ordering
class PlaylistItem(OrderedModel):
    song = models.CharField(max_length=100)
```

## Best Practices

1. Always inherit from BaseModel or its variants instead of models.Model
2. Choose the most specific model type for your needs
3. Use model combinations when you need multiple features
4. Follow the documentation for each model type
5. Consider performance implications when combining features

For detailed documentation on each model type, click the respective links above.
