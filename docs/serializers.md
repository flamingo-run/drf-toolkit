# Serializers

DRF Toolkit extends Django REST Framework's serialization capabilities with enhanced functionality and automatic field handling.

## BaseModelSerializer

The `BaseModelSerializer` is designed to work seamlessly with the BaseModel counterpart, providing enhanced functionality for model serialization.

```python
from drf_kit.serializers import BaseModelSerializer

class UserSerializer(BaseModelSerializer):
    class Meta:
        model = User
        fields = [*BaseModelSerializer.Meta.fields, "name", "email"]
```

### Key Features

- Automatic timezone-aware DateTime field handling
- Built-in read-only fields for `id`, `created_at`, and `updated_at`
- Disabled unique together validators (handled at database level)
- Customized field mapping for better default behavior

## ForeignKeyField

A custom field that extends `PrimaryKeyRelatedField` to add serializer-level validation for foreign key relationships. It supports both single and many-to-many relationships.

```python
from drf_kit.serializers import ForeignKeyField

class UserSerializer(BaseModelSerializer):
    department = ForeignKeyField(queryset=Department.objects.all())
    groups = ForeignKeyField(queryset=Group.objects.all(), m2m=True)

    class Meta:
        model = User
        fields = ['id', 'department', 'groups']
```

### Features

- Write-only by default for better security
- Built-in support for many-to-many relationships
- Automatic primary key conversion
- Proper validation of foreign key constraints

## JSONEncoder

A powerful JSON encoder that extends Django's `DjangoJSONEncoder` to handle additional Python types commonly used in web applications.

### Supported Types

- DateTime objects (with timezone handling)
- Decimal numbers
- TimeZone objects
- Django FileFields (converts to URLs)
- PostgreSQL Range objects
- Objects with `_json()` method
- Objects with `__dict__` attribute

### Example Usage

```python
data = {
    'timestamp': datetime.now(),
    'amount': Decimal('10.50'),
    'timezone': ZoneInfo('UTC'),
    'file': user.avatar,
    'age_range': Range(lower=18, upper=25)
}

serialized = json.dumps(data, cls=JSONEncoder)
```

## Formatting Utilities

DRF Toolkit provides several utilities for consistent data formatting:

### as_str

Converts values to string with special handling for datetime:

```python
from drf_kit.serializers import as_str

# Basic usage
as_str(True)  # Returns "True"
as_str(None)  # Returns None

# DateTime handling
from datetime import datetime, UTC
dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
as_str(dt)  # Returns "2023-01-01T12:00:00Z"

# Non-UTC timezone
from zoneinfo import ZoneInfo
dt = datetime(2023, 1, 1, 12, 0, 0, tzinfo=ZoneInfo("Asia/Hong_Kong"))
as_str(dt)  # Returns "2023-01-01T04:00:00Z" (converted to UTC)
```

### assure_tz

Ensures datetime objects have proper timezone:

```python
from drf_kit.serializers import assure_tz
from datetime import datetime
from zoneinfo import ZoneInfo

# From string
dt_str = "2023-01-01T12:00:00"
dt = assure_tz(dt_str)  # Returns datetime with default timezone

# Custom timezone
dt = datetime(2023, 1, 1, 12, 0, 0)  # naive datetime
dt_hk = assure_tz(dt, tz="Asia/Hong_Kong")  # Returns datetime with Hong Kong timezone

# From existing datetime
dt_utc = datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC)
dt = assure_tz(dt_utc)  # Returns datetime in default timezone
```

### as_dict

Converts objects to dictionary using JSONEncoder:

```python
from drf_kit.serializers import as_dict

# Convert complex objects to dict
data = {
    'date': datetime(2023, 1, 1, 12, 0, 0, tzinfo=UTC),
    'price': Decimal('10.99'),
    'file': user.avatar
}
result = as_dict(data)
# {
#     'date': '2023-01-01T12:00:00Z',
#     'price': '10.99',
#     'file': '/media/avatars/user.jpg'
# }
```

## Best Practices

1. Use `BaseModelSerializer` when working with models that inherit from BaseModel
2. Prefer `ForeignKeyField` over raw `PrimaryKeyRelatedField` for better validation
3. Use `JSONEncoder` when dealing with complex Python objects that need serialization
4. Consider security implications when exposing foreign keys and file fields
5. Always use `assure_tz` when handling datetime objects
6. Use `as_str` for consistent string representation
7. Leverage `as_dict` for complex object serialization

For more detailed information about specific serializer features and advanced usage, refer to the source code documentation.
