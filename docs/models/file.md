# File Models

The File Models in DRF Toolkit provide enhanced file handling capabilities for Django models. The functionality is implemented through the `BoundedFileMixin`, which is included in `BaseModel`.

## BoundedFileMixin

The `BoundedFileMixin` automatically manages file names and storage operations for models with file fields.

```python
from drf_kit.models import BaseModel

class Document(BaseModel):  # Includes BoundedFileMixin
    file = models.FileField(upload_to='documents/')
    title = models.CharField(max_length=100)
```

### Features

- Automatic file name management
- Support for custom storage backends
- Efficient file operations
- Proper file cleanup
- Handles multiple file fields

### File Management

The mixin manages files during model creation:

1. Generates proper file names using the field's `upload_to` and file name generator
2. Moves files to their final location
3. Updates file references in the model
4. Handles cleanup of temporary files

### Storage Backend Support

The mixin works with different storage backends:

```python
class Document(BaseModel):
    # Local filesystem storage
    local_file = models.FileField(
        upload_to='local/',
        storage=FileSystemStorage()
    )
    
    # Custom storage backend
    cloud_file = models.FileField(
        upload_to='cloud/',
        storage=CustomStorageBackend()
    )
```

#### Storage Operations

- Uses `move` operation when available (more efficient)
- Falls back to save/delete for basic storage backends
- Properly closes file handles after operations

## Usage Examples

### Basic File Handling

```python
class UserDocument(BaseModel):
    file = models.FileField(upload_to='user_docs/')
    user = models.ForeignKey(User, on_delete=models.CASCADE)

# File will be automatically managed
doc = UserDocument.objects.create(
    file=uploaded_file,
    user=user
)
```

### Custom File Naming

```python
def generate_filename(instance, filename):
    return f"documents/{instance.user.id}/{filename}"

class Document(BaseModel):
    file = models.FileField(upload_to=generate_filename)
```

### Multiple File Fields

```python
class MediaItem(BaseModel):
    image = models.ImageField(upload_to='images/')
    document = models.FileField(upload_to='documents/')
    attachment = models.FileField(upload_to='attachments/')
    
    # All files will be properly managed
```

### Custom Storage Backend

```python
class S3Document(BaseModel):
    file = models.FileField(
        upload_to='documents/',
        storage=S3Boto3Storage()
    )
    
    # Files will be efficiently moved in S3
    # if the storage backend supports move operations
```

## Best Practices

1. Always use the mixin (through BaseModel) when working with file fields
2. Implement proper file name generators for organized storage
3. Use storage backends that support move operations for better performance
4. Consider implementing file cleanup on model deletion if needed
5. Handle file operations in transactions when appropriate

## Technical Details

### File Operations

The mixin performs these steps during model creation:

1. Saves the model instance first
2. Identifies all FileField instances
3. For each file:
   - Generates the final filename
   - Moves/copies the file if needed
   - Updates the file reference
4. Saves the model again if files were modified

### Storage Backend Integration

```python
# With move support
if hasattr(file.storage, "move"):
    file.storage.move(old_file, new_file)
else:
    # Fallback for basic storage
    file.storage.save(new_file, file)
    file.storage.delete(old_file)
```

This ensures compatibility with both simple and advanced storage backends.