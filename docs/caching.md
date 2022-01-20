# Caching

DRF Toolkit provides a flexible caching system with robust cache key generation and support for cache directives.

## Enabling Cache

Enable caching in your viewsets by using the pre-built cached viewsets from drf_kit:

```python
from drf_kit.viewsets import CachedModelViewSet

class UserViewSet(CachedModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    cache_timeout = 300  # Cache for 5 minutes
```

## Cache Key Generation

The toolkit uses a robust `CacheKeyConstructor` that generates unique cache keys based on:
- Unique view method identifier
- URL arguments
- URL keyword arguments
- Query parameters (including handling of multiple values)
- Request's accepted media type

### Configuration

You can configure the cache key generation function globally in your settings:

```python
REST_FRAMEWORK_EXTENSIONS = {
    'DEFAULT_CACHE_KEY_FUNC':
        'drf_kit.cache.cache_key_constructor'
}
```

## Cache Directives

The caching system respects HTTP cache control directives. Currently supported:

- `no-cache`: Forces a fresh response, bypassing the cache
- When cache is used, responses include:
  - `Expires` header with the expiration timestamp
  - `Cache-Control: max-age=<timeout>` header
  - `X-Cache: HIT/MISS` header indicating cache status

## Advanced Usage

### Custom Cache Timeout

You can customize the cache timeout per viewset:

```python
class UserViewSet(CachedModelViewSet):
    cache_timeout = 3600  # Cache for 1 hour
```

### Custom Cache Key Constructor

While the default `CacheKeyConstructor` is suitable for most cases, you can create your own key constructor by extending it:

```python
from drf_kit.cache import CacheKeyConstructor
from rest_framework_extensions.key_constructor import bits

class CustomCacheKeyConstructor(CacheKeyConstructor):
    # Add custom bits for key generation
    user_id = bits.UserKeyBit()

custom_cache_key_constructor = CustomCacheKeyConstructor()

class UserViewSet(CachedModelViewSet):
    cache_key_constructor = custom_cache_key_constructor
```

## Best Practices

1. Choose appropriate cache timeouts:
   - Short for frequently changing data
   - Longer for stable data
   - Consider user-specific needs
