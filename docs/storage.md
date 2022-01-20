# Storage Utilities

DRF Toolkit provides storage utilities to help manage file storage paths and naming conventions in your Django applications.

## BaseDataStoragePath

The `BaseDataStoragePath` class provides utilities for handling file storage paths and file naming. It's particularly useful when you need consistent file naming conventions and unique file paths in your storage system.

### Features

- Automatic unique file naming using UUID
- File extension handling
- Flexible path building
- Support for both model instances and dictionaries

### Basic Usage

```python
from drf_kit.storage import BaseDataStoragePath

# Rename a file with unique suffix
new_filename = BaseDataStoragePath.rename(
    filename="document.pdf",
    unique=True
)
# Result: document_550e8400-e29b-41d4-a716-446655440000.pdf

# Rename with custom name
new_filename = BaseDataStoragePath.rename(
    filename="document.pdf",
    new_name="contract",
    unique=True
)
# Result: contract_550e8400-e29b-41d4-a716-446655440000.pdf
```

### File Extension Handling

The class handles file extensions intelligently:

```python
# With existing extension
filename = BaseDataStoragePath.rename(
    filename="document.pdf",
    new_name="contract"
)
# Result: contract.pdf

# With default extension
filename = BaseDataStoragePath.rename(
    filename="document",
    new_name="contract",
    default_extension="txt"
)
# Result: contract.txt

# Without extension
filename = BaseDataStoragePath.rename(
    filename="document",
    new_name="contract"
)
# Result: contract (with warning log)
```

### Custom Storage Path

You can extend the class for custom storage paths:

```python
class UserAvatarStorage(BaseDataStoragePath):
    @classmethod
    def get_upload_path(cls, instance, filename):
        user_id = cls._get_pk(instance)
        new_filename = cls.rename(filename, unique=True)
        return f"avatars/{user_id}/{new_filename}"

# Usage with model
class UserProfile(models.Model):
    avatar = models.ImageField(
        upload_to=UserAvatarStorage.get_upload_path
    )
```

### Primary Key Handling

The class handles primary keys for both model instances and dictionaries:

```python
# With model instance
profile = UserProfile.objects.get(id=1)
pk = BaseDataStoragePath._get_pk(profile)  # Returns "1"

# With dictionary
data = {"id": "123"}
pk = BaseDataStoragePath._get_pk(data)  # Returns "123"

# With new instance (generates UUID)
new_profile = UserProfile()
pk = BaseDataStoragePath._get_pk(new_profile)  # Returns UUID string
```

## Best Practices

1. Use unique filenames when storing user-uploaded files to prevent collisions
2. Create custom storage classes for different types of files (e.g., avatars, documents)
3. Always handle file extensions appropriately
4. Consider implementing cleanup methods for old files
5. Use the storage utilities with Django's file fields for consistent handling