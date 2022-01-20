# Views

DRF Toolkit provides enhanced viewsets with built-in support for multiple serializers, caching, searching, and bulk operations.

## ModelViewSet

The base viewset class extends DRF's ModelViewSet with additional functionality for handling different serializers per action:

```python
from drf_toolkit.views import ModelViewSet

class UserViewSet(ModelViewSet):
    queryset = User.objects.all()

    # Different serializers for different actions
    serializer_class = UserDefaultSerializer
    serializer_detail_class = UserDetailSerializer
    serializer_create_class = UserCreateSerializer
    serializer_update_class = UserUpdateSerializer
    serializer_list_class = UserListSerializer

    # Different querysets for different actions
    queryset_detail = User.objects.select_related('profile')
    queryset_create = User.objects.all()
    queryset_update = User.objects.select_for_update()
```

### Key Features

- Multiple serializers per action (detail, list, create, update)
- Different querysets per action
- Supports GET, POST, PATCH, DELETE methods
- Automatic response serializer selection

### Variants

#### ReadOnlyModelViewSet

For read-only endpoints that only allow GET operations:

```python
from drf_toolkit.views import ReadOnlyModelViewSet

class UserViewSet(ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Only GET, HEAD, OPTIONS methods allowed
```

#### NonDestructiveModelViewSet

For endpoints that don't allow deletion:

```python
from drf_toolkit.views import NonDestructiveModelViewSet

class UserViewSet(NonDestructiveModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Allows GET, POST, PATCH methods, but no DELETE
```

#### WriteOnlyModelViewSet

For write-only endpoints:

```python
from drf_toolkit.views import WriteOnlyModelViewSet

class UserViewSet(WriteOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    # Only POST, PATCH, DELETE methods allowed
```

## Cached Viewsets

### CachedModelViewSet

Adds automatic caching to list and retrieve operations:

```python
from drf_toolkit.views import CachedModelViewSet

class UserViewSet(CachedModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

Key features:
- Automatic cache key generation based on:
  - View ID
  - URL parameters
  - Query parameters
  - Request headers
- Respects Cache-Control headers
- Adds X-Cache header (HIT/MISS)
- Sets Expires header

Variants:
- CachedReadOnlyModelViewSet
- CachedNonDestructiveModelViewSet

### CachedSearchableModelViewSet

Implements searching capabilities using POST body with caching:

```python
from drf_toolkit.views import CachedSearchableModelViewSet

class UserViewSet(CachedSearchableModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    search_fields = ['username', 'email']
```

Key features:
- POST-based search endpoint
- Cache keys include request body
- All features from CachedModelViewSet

Variants:
- CachedSearchableReadOnlyModelViewSet
- CachedSearchableNonDestructiveModelViewSet

## Additional Mixins

### UpsertMixin

Handles duplicate records by updating instead of creating:

```python
from drf_toolkit.views import ModelViewSet, UpsertMixin

class UserViewSet(UpsertMixin, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
```

Key features:
- Catches IntegrityError and ConflictException
- Updates existing record if found
- Returns HTTP 200 for upserts
- Handles both database and application-level conflicts

### BulkMixin

Enables bulk operations:

```python
from drf_toolkit.views import ModelViewSet, BulkMixin

class UserViewSet(BulkMixin, ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    serializer_list_class = UserBulkSerializer
```

Key features:
- Enables bulk create and update
- Uses list serializers for responses
- Disables individual PATCH operations
- Supports different serializers for bulk operations

## Best Practices

1. Choose the appropriate viewset variant for your use case
2. Use specific serializers for different actions when needed
3. Consider caching for read-heavy endpoints
4. Use UpsertMixin when dealing with potential duplicates
5. Implement BulkMixin for batch operations
6. Set appropriate cache control headers for cached endpoints
7. Use CachedSearchableModelViewSet for complex search operations

## Nested Views

DRF Toolkit provides specialized viewsets for handling nested resources (Many-to-One relationships):

```python
from drf_toolkit.views import NestedModelViewSet

class CommentViewSet(NestedModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    # Parent model configuration
    queryset_nest = Post.objects.all()
    lookup_url_kwarg_nest = 'post_pk'  # URL parameter for parent ID
    lookup_field_nest = 'post_id'      # Field name in Comment model
    serializer_field_nest = 'post'     # Field name in serializer
```

### Key Features

- Automatically filters child objects by parent
- Validates parent-child relationships
- Injects parent relationship in create/update operations
- Handles URL-based parent identification

### Variants

- **NestedModelViewSet**: Full CRUD operations for nested resources
- **CachedNestedModelViewSet**: Adds caching support
- **ReadOnlyNestedModelViewSet**: Read-only operations
- **CachedReadOnlyNestedModelViewSet**: Read-only with caching

## Single Nested Views

For handling One-to-One relationships, use Single Nested Views:

```python
from drf_toolkit.views import SingleNestedModelViewSet

class ProfileViewSet(SingleNestedModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    queryset_nest = User.objects.all()
    lookup_url_kwarg_nest = 'user_pk'
    lookup_field_nest = 'user_id'
```

### Key Features

- Enforces single object constraint
- Collection-level operations (no PK-based endpoints)
- PUT method to replace existing relationship
- Automatic conflict detection

### Variants

- **SingleNestedModelViewSet**: Full CRUD operations
- **CachedSingleNestedModelViewSet**: Adds caching support
- **ReadOnlySingleNestedModelViewSet**: Read-only operations
- **CachedReadOnlySingleNestedModelViewSet**: Read-only with caching

## Stats View Mixin

The StatsViewMixin allows dynamic queryset mutation and serializer switching based on a query parameter:

```python
from drf_toolkit.views import ModelViewSet, StatsViewMixin

class OrderViewSet(StatsViewMixin, ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    serializer_stats_class = OrderStatsSerializer

    def add_stats_to_queryset(self, queryset):
        return queryset.annotate(
            total_items=Count('items'),
            total_value=Sum('items__price')
        )
```

### Key Features

- Activates with `?stats=1` query parameter
- Supports custom queryset annotations
- Uses different serializer for stats view
- Preserves original queryset ordering
