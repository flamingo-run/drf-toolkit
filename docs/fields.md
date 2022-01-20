# Custom Fields

DRF Toolkit provides custom fields that extend Django's built-in fields with additional functionality.

## DefaultTimezoneDateTimeField

A custom DateTime field that ensures consistent timezone handling by always using the project's default timezone (`settings.TIME_ZONE`), regardless of the current request's timezone context.

This is particularly useful when you want to ensure that datetime fields are always handled in the project's default timezone, preventing issues with middleware or context-specific timezone changes.

### Usage

```python
from drf_kit.fields import DefaultTimezoneDateTimeField
from rest_framework import serializers

class EventSerializer(serializers.ModelSerializer):
    created_at = DefaultTimezoneDateTimeField()
    scheduled_at = DefaultTimezoneDateTimeField(required=False)

    class Meta:
        model = Event
        fields = ['id', 'created_at', 'scheduled_at']
```

### Key Features

- Always uses the project's default timezone from settings
- Prevents timezone inconsistencies from middleware or context changes
- Compatible with Django REST Framework's datetime handling

## SlugifyField

An enhanced version of Django's SlugField that automatically applies slugification to the field value before saving. It allows customization of the slugify function used.

### Usage

```python
from drf_kit.fields import SlugifyField
from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=100)
    slug = SlugifyField(max_length=100)  # Will automatically slugify from title
```

### Custom Slugify Function

You can provide a custom slugify function:

```python
def custom_slugify(value):
    # Your custom slugification logic
    return value.lower().replace(' ', '-')

class Article(models.Model):
    title = models.CharField(max_length=100)
    slug = SlugifyField(max_length=100, func=custom_slugify)
```

### Parameters

- `max_length` (int): Maximum length for the slug (default: 50)
- `db_index` (bool): Whether to create a database index (default: True)
- `allow_unicode` (bool): Whether to allow unicode characters in slugs (default: False)
- `func` (callable): Custom slugify function (default: django.utils.text.slugify)

### Example with All Options

```python
class Article(models.Model):
    title = models.CharField(max_length=100)
    slug = SlugifyField(
        max_length=100,
        db_index=True,
        allow_unicode=True,
        func=custom_slugify
    )
```

## Best Practices

1. Use `DefaultTimezoneDateTimeField` when you need consistent timezone handling across your application
2. Use `SlugifyField` for automatic URL-friendly slug generation
3. Consider providing custom slugify functions when you need special slug formatting
4. Remember to handle edge cases in custom slugify functions