# Base Models

The Base Models in DRF Toolkit provide fundamental functionality that all other models build upon. These models include essential features like automatic timestamps, change tracking, and file handling capabilities.

## BaseModel

The `BaseModel` is the foundation for all models in DRF Toolkit. It combines several mixins to provide a rich set of features while maintaining clean and organized code.

```python
from drf_kit.models import BaseModel

class MyModel(BaseModel):
    name = models.CharField(max_length=100)
```

### Features

#### Automatic Timestamps
- `created_at`: Automatically set when the object is created
- `updated_at`: Automatically updated whenever the object is saved

#### Default Configuration
- Ordering by most recently updated (`-updated_at`)
- Automatic indexing on `updated_at` field
- Latest object determination based on `updated_at`


### Change Tracking

BaseModel includes the ModelDiffMixin (see [Diff Models](diff.md) for details) which provides:

```python
# Create and modify an object
obj = MyModel.objects.create(name="Original")
obj.name = "Modified"

# Check what changed
obj._has_changed  # True
obj._changed_fields  # ['name']
obj._diff  # {'name': ('Original', 'Modified')}

# Save changes
obj.save()  # Resets the change tracking
obj._has_changed  # False
```

### File Handling

BaseModel includes BoundedFileMixin for enhanced file field management (see [File Models](file.md) for details).

## Usage Examples

### Basic Usage

```python
from drf_kit.models import BaseModel
from django.db import models

class Product(BaseModel):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)

# Create a product
product = Product.objects.create(
    name="Widget",
    price=9.99
)

# Automatic timestamps
print(product.created_at)  # When the product was created
print(product.updated_at)  # When the product was last modified

# Get admin URL
admin_url = product.admin_edit_url()
```

### Querying

```python
# Get latest products
latest_products = Product.objects.all()  # Automatically ordered by -updated_at

# Get single latest product
latest_product = Product.objects.latest()

# Use the timestamp index
recent_products = Product.objects.filter(
    updated_at__gte=timezone.now() - timedelta(days=7)
)
```

## Best Practices

1. Always inherit from BaseModel instead of models.Model for consistent functionality
2. Use the provided change tracking methods instead of manual state comparison
3. Leverage the automatic timestamps for tracking object history
4. Take advantage of the default ordering and indexes for common query patterns
5. Use the admin_edit_url() method for admin panel integration