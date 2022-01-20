# Diff Models

The Diff Models in DRF Toolkit provide functionality for tracking changes to model instances. This is particularly useful for audit logging, change history, and validation scenarios.

## ModelDiffMixin

The `ModelDiffMixin` tracks changes to model fields by maintaining a snapshot of the initial state and comparing it with current values.

```python
from drf_kit.models import BaseModel  # Includes ModelDiffMixin

class User(BaseModel):
    name = models.CharField(max_length=100)
    email = models.EmailField()
```

### Features

- Tracks changes to model fields
- Supports relationship fields
- Handles deferred fields (lazy loading)
- Automatic state reset after save
- Serializable diff format

### Properties and Methods

#### `_has_changed`
Returns `True` if any field has changed from its initial state.

```python
user = User.objects.create(name="John", email="john@example.com")
user.name = "Johnny"
print(user._has_changed)  # True
```

#### `_changed_fields`
Returns a list of field names that have changed.

```python
user.name = "Johnny"
user.email = "johnny@example.com"
print(user._changed_fields)  # ['name', 'email']
```

#### `_diff`
Returns a dictionary of changed fields with their original and new values.

```python
user.name = "Johnny"
print(user._diff)  # {'name': ('John', 'Johnny')}
```

#### `_get_field_diff(field_name)`
Returns the change tuple (old_value, new_value) for a specific field.

```python
old_value, new_value = user._get_field_diff('name')
```

### State Management

The initial state is captured when:
1. The object is instantiated
2. After a successful save
3. When refreshed from the database

```python
# Create a user
user = User.objects.create(name="John")
print(user._has_changed)  # False

# Modify the user
user.name = "Johnny"
print(user._has_changed)  # True
print(user._diff)  # {'name': ('John', 'Johnny')}

# Save the user
user.save()
print(user._has_changed)  # False (state reset after save)
```

### Relationship Fields

For relationship fields, the mixin tracks the foreign key ID:

```python
class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)

post = Post.objects.create(author=user, title="Hello")
post.author = other_user
print(post._diff)  # {'author_id': (1, 2)}
```

### Deferred Fields

The mixin handles deferred fields (from `defer()` or `only()` queries) by lazy loading them when needed:

```python
# Only load specific fields
user = User.objects.only('name').get(id=1)
print(user.email)  # Triggers lazy loading
print(user._diff)  # Includes changes to all fields
```

## Usage Examples

### Audit Logging

```python
class AuditedModel(BaseModel):
    def save(self, *args, **kwargs):
        if self._has_changed:
            AuditLog.objects.create(
                model=self.__class__.__name__,
                object_id=self.pk,
                changes=self._diff
            )
        super().save(*args, **kwargs)
```

### Validation

```python
class User(BaseModel):
    def clean(self):
        if 'email' in self._changed_fields:
            # Validate email change
            validate_email_change(self._get_field_diff('email'))
```

### Change Detection

```python
def update_user(user, **changes):
    for field, value in changes.items():
        setattr(user, field, value)
    
    if user._has_changed:
        user.save()
        notify_user_changed(user, user._diff)
    return user
```

## Best Practices

1. Use `_has_changed` for conditional logic based on changes
2. Access specific field changes with `_get_field_diff()` instead of parsing `_diff`
3. Remember that `save()` resets the change tracking
4. Consider performance implications when using with deferred fields
5. Use the change tracking for audit logs and validation scenarios