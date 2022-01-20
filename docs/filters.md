# Filters

DRF Toolkit provides powerful filtering capabilities with custom filter types and filter backends designed to handle common filtering scenarios efficiently.

## FilterBackend

A custom filter backend that provides better error handling by converting `ValueError` and `AttributeError` exceptions into HTTP 400 responses with clear error messages.

You can configure the FilterBackend at the settings level for all viewsets:

```python
# settings.py
REST_FRAMEWORK = {
    'DEFAULT_FILTER_BACKENDS': ['drf_kit.filters.FilterBackend']
}
```

Or configure it at the viewset level for specific views:

```python
from drf_kit.filters import FilterBackend

class UserViewSet(ModelViewSet):
    filter_backends = [FilterBackend]
    filterset_class = UserFilterSet
```

## Filter Types

### IntBooleanFilter

A filter that converts integer values (0/1) to boolean filters. Useful for boolean fields in querystrings.

```python
from drf_kit.filters import IntBooleanFilter, FilterSet

class UserFilterSet(FilterSet):
    is_active = IntBooleanFilter()

# Usage:
# GET /api/users/?is_active=1  # Returns active users
# GET /api/users/?is_active=0  # Returns inactive users
```

### AnyOfFilter

Performs an OR operation when multiple values are provided for the same field. Values are provided by repeating the query parameter.

```python
from drf_kit.filters import AnyOfFilter, FilterSet

class UserFilterSet(FilterSet):
    status = AnyOfFilter()

# Usage:
# GET /api/users/?status=active&status=pending  # Returns users with status active OR pending
```

### AllOfFilter

Similar to AnyOfFilter but performs an AND operation. Must be used with `conjoined=True`.

```python
from drf_kit.filters import AllOfFilter, FilterSet

class UserFilterSet(FilterSet):
    roles = AllOfFilter()  # conjoined=True by default

# Usage:
# GET /api/users/?roles=admin&roles=moderator  # Returns users that have BOTH roles
```

### AnyOfOrNullFilter

Extends AnyOfFilter to handle null values. Use "null" as a special keyword to filter for null values.

```python
from drf_kit.filters import AnyOfOrNullFilter, FilterSet

class UserFilterSet(FilterSet):
    supervisor = AnyOfOrNullFilter()

# Usage:
# GET /api/users/?supervisor=null  # Returns users with no supervisor
# GET /api/users/?supervisor=123&supervisor=null  # Returns users with supervisor_id=123 OR no supervisor
```

## BaseFilterSet

A FilterSet that allows setting default/initial values for filters. The initial value can be a static value or a callable.

```python
from drf_kit.filters import BaseFilterSet, IntBooleanFilter

class UserFilterSet(BaseFilterSet):
    is_active = IntBooleanFilter(initial=1)  # Static initial value
    department = CharFilter(initial=lambda request: request.user.department)  # Callable initial value

    class Meta:
        model = User
        fields = ['is_active', 'department']

# Usage:
# GET /api/users/  # By default, returns only active users
# GET /api/users/?is_active=0  # Overrides default and returns inactive users
```

## Best Practices

1. Use `FilterBackend` to get better error handling with 400 responses for invalid filter values
2. Choose appropriate filter types based on your filtering needs:
   - `IntBooleanFilter` for boolean fields
   - `AnyOfFilter` for OR operations
   - `AllOfFilter` for AND operations
   - `AnyOfOrNullFilter` when null values need special handling
3. Use `BaseFilterSet` when you need default filter values
