# Soft Delete Models

The Soft Delete Models in DRF Toolkit provide functionality for marking records as deleted without physically removing them from the database. This is particularly useful for maintaining data history, implementing recycle bins, or handling complex relationships.

## SoftDeleteModel

The `SoftDeleteModel` adds soft deletion capabilities to your models, maintaining a deletion timestamp and managing related objects.

```python
from drf_kit.models import SoftDeleteModel

class Document(SoftDeleteModel):
    title = models.CharField(max_length=100)
    content = models.TextField()
```

### Features

- Soft deletion with timestamp tracking
- Undelete capability
- Prevention of updates to deleted records
- Automatic filtering of deleted records
- Cascade and SET_NULL support for related objects
- Custom manager with additional query methods
- Pre/post signals for delete and undelete operations

### Deletion Field

The model includes a `deleted_at` field that tracks deletion time:

```python
deleted_at = models.DateTimeField(
    blank=True,
    null=True,
    default=None
)
```

## Usage Examples

### Basic Operations

```python
# Create and delete a document
doc = Document.objects.create(title="Important", content="...")
doc.delete()  # Soft delete (sets deleted_at)

# Check deletion status
print(doc.is_deleted)  # True
print(doc.deleted_at)  # Current timestamp

# Try to update deleted document
doc.title = "New Title"
doc.save()  # Raises UpdatingSoftDeletedException

# Undelete the document
doc.undelete()
print(doc.is_deleted)  # False
print(doc.deleted_at)  # None

# Hard delete (actual removal)
doc.delete()  # First soft delete
doc.delete()  # Second delete removes from database
```

### Querying

```python
# Default manager excludes deleted records
active_docs = Document.objects.all()

# Include deleted records
all_docs = Document.objects.all_with_deleted()

# Bulk operations
Document.objects.filter(title__contains="draft").delete()  # Soft delete
Document.objects.filter(title__contains="old").hard_delete()  # Actually delete
```

### Related Objects

#### Many-to-Many Relationships

The soft delete manager automatically handles soft-deleted objects in M2M relationships:

```python
class Team(SoftDeleteModel):
    name = models.CharField(max_length=100)
    members = models.ManyToManyField('User', through='TeamMembership')

class TeamMembership(SoftDeleteModel):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    user = models.ForeignKey('User', on_delete=models.CASCADE)

# Queries will automatically exclude soft-deleted memberships
active_teams = Team.objects.filter(members__username="john")
```

To control this behavior, configure the `SOFT_DELETE_M2M_EXCLUDE_DELETED` setting:
```python
# settings.py
SOFT_DELETE_M2M_EXCLUDE_DELETED = True  # Default: False
```

#### Cascade Deletion

```python
class Newspaper(SoftDeleteModel):
    name = models.CharField(max_length=100)

class Article(SoftDeleteModel):
    newspaper = models.ForeignKey(
        Newspaper,
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=100)

# When newspaper is deleted, articles are soft deleted too
newspaper = Newspaper.objects.create(name="Daily Prophet")
Article.objects.create(newspaper=newspaper, title="Breaking News")
newspaper.delete()  # Article is also soft deleted
```

#### SET_NULL Handling

```python
class News(SoftDeleteModel):
    newspaper = models.ForeignKey(
        Newspaper,
        on_delete=models.SET_NULL,
        null=True
    )
    title = models.CharField(max_length=100)

# When newspaper is deleted, news references are set to null
newspaper = Newspaper.objects.create(name="Daily Prophet")
news = News.objects.create(newspaper=newspaper, title="Event")
newspaper.delete()  # news.newspaper becomes None
```

### Signal Handling

```python
from drf_kit.signals import pre_soft_delete, post_soft_delete
from drf_kit.signals import pre_undelete, post_undelete

def handle_pre_delete(sender, instance, **kwargs):
    print(f"About to delete {instance}")

def handle_post_delete(sender, instance, **kwargs):
    print(f"Deleted {instance}")

pre_soft_delete.connect(handle_pre_delete, sender=Document)
post_soft_delete.connect(handle_post_delete, sender=Document)
```

## Technical Details

### Custom Manager

```python
class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

    def all_with_deleted(self):
        return super().get_queryset()

    def hard_delete(self):
        return super().get_queryset().delete()
```

### Deletion Prevention

```python
def verify_soft_deletion(sender, instance, **kwargs):
    if instance.is_deleted and not instance._state.adding:
        raise exceptions.UpdatingSoftDeletedException()
```

## Best Practices

1. Use SoftDeleteModel when you need to maintain deleted records
2. Handle both soft-deleted and active records in your business logic
3. Use signals for audit logging or related operations
4. Consider storage implications of keeping deleted records
5. Use hard delete for actual cleanup when needed
6. Remember that unique constraints apply to both active and deleted records
7. Consider implementing cleanup policies for old deleted records
