# Pagination

DRF Toolkit provides enhanced pagination capabilities that extend Django REST Framework's built-in pagination classes. Our implementation focuses on flexibility and performance optimization.

## Available Pagination Classes

### CustomPagePagination

The `CustomPagePagination` class extends DRF's `PageNumberPagination` with additional customization options:

```python
from drf_kit.pagination import CustomPagePagination

class MyPagination(CustomPagePagination):
    page_size = 100
    page_size_query_param = 'page_size'  # Allow client to override page size
    page_start = 1  # Default is 1, but can be customized
```

Key features:
- Customizable starting page number (default: 1)
- Dynamic page size through query parameters
- Smart URL handling:
  - First page: removes page parameter entirely (e.g., /api/users/)
  - Other pages: includes page number (e.g., /api/users/?page=2)
- Full compatibility with DRF's browsable API including pagination controls
- Proper handling of edge cases (invalid pages, empty results)

Usage example:
```python
# In your viewset
from rest_framework.viewsets import ModelViewSet

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    pagination_class = MyPagination
```

API requests:
```
GET /api/users/           # First page (when page_start = 1)
GET /api/users/?page=2    # Second page
GET /api/users/?page_size=50  # Custom page size
```

Response format:
```json
{
    "count": 100,
    "next": "http://api.example.org/users/?page=2",
    "previous": "http://api.example.org/users/?page=1",
    "results": []
}
```

### LightPagePagination

The `LightPagePagination` is a lighter version of `CustomPagePagination` that omits the total count query, making it more efficient for large datasets:

```python
from drf_kit.pagination import LightPagePagination

class FastPagination(LightPagePagination):
    page_size = 100
    page_size_query_param = 'page_size'
    page_start = 1
```

Key features:
- Inherits all customization options from CustomPagePagination
- Removes the expensive COUNT query for better performance
- Smart next page detection:
  - Has next page if current page size equals requested page size
  - No additional query needed for this check
- Maintains proper URL handling and browsable API support
- Ideal for large datasets where total count isn't necessary or too expensive

Response format:
```json
{
    "next": "http://api.example.org/users/?page=2",
    "previous": "http://api.example.org/users/?page=1",
    "results": []
}
```

## Configuration

### Global Configuration

To set a default pagination class for all viewsets, add to your Django settings:

```python
REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS': 'drf_kit.pagination.CustomPagePagination',
    'PAGE_SIZE': 100
}
```

### Per-View Configuration

Override pagination for specific viewsets:

```python
from drf_kit.pagination import LightPagePagination

class UserViewSet(ModelViewSet):
    pagination_class = LightPagePagination
    page_size = 50
```

## Best Practices

1. Choose the appropriate pagination class:
   - Use `CustomPagePagination` when you need total count
   - Use `LightPagePagination` for large datasets or better performance

2. Configure reasonable limits:
   - Set appropriate page sizes
   - Consider your data volume and access patterns
   - Use page_size_query_param wisely

