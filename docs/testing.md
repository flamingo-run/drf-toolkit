# Testing

DRF Toolkit provides a comprehensive testing framework through the `BaseApiTest` class, which extends Django REST framework's `APITransactionTestCase`. This class offers a wide range of testing utilities specifically designed for API testing.

## Base API Test Class

The `BaseApiTest` class is the foundation for API testing in DRF Toolkit. To use it, extend your test class from `BaseApiTest`:

```python
from drf_kit.tests import BaseApiTest

class MyAPITest(BaseApiTest):
    def test_my_api(self):
        response = self.client.get('/api/endpoint/')
        self.assertResponse(status.HTTP_200_OK, response)
```

## Cache Testing

### Real Cache Context Manager

The `real_cache` context manager allows testing with a local memory cache:

```python
def test_with_cache(self):
    with self.real_cache():
        # Test code that uses cache
        response = self.client.get('/api/cached-data/')
        self.assertResponse(status.HTTP_200_OK, response)
```

### Cache Lock Testing

Test cache locks using the `patch_cache_lock` context manager:

```python
def test_locked_operation(self):
    with self.patch_cache_lock() as lock:
        # Execute code that uses cache lock
        result = some_locked_operation()
        
        # Assert lock was called with specific parameters
        lock.assert_called_with("lock_name", timeout=60)
```

## Migration Testing

Check for pending migrations using `assertNoPendingMigration`:

```python
def test_migrations(self):
    self.assertNoPendingMigration("my_app")
```

## File Path Testing

Validate UUID-based file paths using `assertUUIDFilePath`:

```python
def test_file_path(self):
    file_path = "uploads/123/image_550e8400-e29b-41d4-a716-446655440000.jpg"
    self.assertUUIDFilePath(
        prefix="uploads",
        pk="123",
        name="image",
        extension="jpg",
        file=file_path
    )
```

## Response Testing

### Basic Response Assertions

```python
def test_api_responses(self):
    # Test list endpoint
    response = self.client.get('/api/items/')
    self.assertResponseList(
        expected_items=[{'id': 1, 'name': 'Item 1'}],
        response=response
    )

    # Test detail endpoint
    response = self.client.get('/api/items/1/')
    self.assertResponseDetail(
        expected_item={'id': 1, 'name': 'Item 1'},
        response=response
    )

    # Test create endpoint
    response = self.client.post('/api/items/', {'name': 'New Item'})
    self.assertResponseCreate(
        expected_item={'id': 2, 'name': 'New Item'},
        response=response
    )

    # Test update endpoint
    response = self.client.put('/api/items/1/', {'name': 'Updated Item'})
    self.assertResponseUpdate(
        expected_item={'id': 1, 'name': 'Updated Item'},
        response=response
    )

    # Test delete endpoint
    response = self.client.delete('/api/items/1/')
    self.assertResponseDelete(response)
```

### Error Response Assertions

```python
def test_error_responses(self):
    # Test bad request
    response = self.client.post('/api/items/', {})
    self.assertResponseBadRequest(response)

    # Test method not allowed
    response = self.client.put('/api/items/')
    self.assertResponseNotAllowed(response)

    # Test authentication required
    response = self.client.get('/api/protected/')
    self.assertResponseNotAuthenticated(response)

    # Test permission denied
    response = self.client.get('/api/admin-only/')
    self.assertResponseForbidden(response)

    # Test not found
    response = self.client.get('/api/items/999/')
    self.assertResponseNotFound(response)
```

### Response Items Testing

Test response items by their IDs:

```python
def test_response_items(self):
    items = [{'id': 1}, {'id': 2}, {'id': 3}]
    response = self.client.get('/api/items/')
    self.assertResponseItems(
        expected_items=[1, 2, 3],  # Can be IDs, objects, or dictionaries
        response=response,
        response_key="results",  # Default is "results"
        pk_field="id"  # Default is "id"
    )
```

### Advanced Response Matching

The `assertResponseMatch` method provides powerful dictionary assertion capabilities:

```python
def test_response_matching(self):
    response = self.client.get('/api/complex-data/')
    
    # Match exact values
    self.assertResponseMatch(
        expected={'name': 'Test', 'count': 42},
        received=response.json()
    )

    # Use regex patterns
    self.assertResponseMatch(
        expected={'code': re.compile(r'^\d{4}$')},
        received={'code': '1234'}
    )

    # Match nested structures
    self.assertResponseMatch(
        expected={
            'user': {
                'id': 1,
                'profile': {
                    'age': 25
                }
            }
        },
        received=response.json()
    )

    # Match lists with specific order
    self.assertResponseMatch(
        expected={'items': [1, 2, 3]},
        received={'items': [1, 2, 3]}
    )

    # Match sets (order doesn't matter)
    self.assertResponseMatch(
        expected={'tags': {'red', 'blue'}},
        received={'tags': ['blue', 'red']}
    )
```

The `assertResponseMatch` method provides detailed error messages when assertions fail, making it easier to identify mismatches in complex data structures.

## Best Practices

1. Use the appropriate assertion method for each type of response
2. Take advantage of the powerful `assertResponseMatch` for complex response validation
3. Use cache testing utilities when working with cached views
4. Always check for pending migrations in your tests
5. Use the provided file path assertions when working with file uploads

For more examples, check the test files in the project, particularly `test_app/tests/test_test_helpers.py`.