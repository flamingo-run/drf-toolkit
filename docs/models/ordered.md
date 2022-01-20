# Ordered Models

The Ordered Models in DRF Toolkit provide functionality for maintaining ordered collections of objects. This is particularly useful for scenarios like rankings, playlists, or any situation where items need to maintain a specific sequence.

## OrderedModel

The `OrderedModel` automatically manages the ordering of objects, ensuring a continuous sequence and providing methods for reordering.

```python
from drf_kit.models import OrderedModel

class Playlist(OrderedModel):
    name = models.CharField(max_length=100)
    song = models.ForeignKey('Song', on_delete=models.CASCADE)
```

### Features

- Automatic order management
- Continuous sequence maintenance
- Support for group-based ordering
- Reordering capabilities
- Index optimization

### Order Field

The model includes an `order` field that maintains the sequence:

```python
order = models.PositiveIntegerField(
    db_index=True,
    default=None,
    null=True,
    blank=True
)
```

## Usage Examples

### Basic Ordering

```python
# Items are automatically ordered as they're created
first = Playlist.objects.create(name="First Song", song=song1)
second = Playlist.objects.create(name="Second Song", song=song2)
third = Playlist.objects.create(name="Third Song", song=song3)

print(first.order)   # 0
print(second.order)  # 1
print(third.order)   # 2

# Get items in order
playlist = Playlist.objects.all()  # Ordered by 'order' field
```

### Group-Based Ordering

```python
class TournamentRanking(OrderedModel):
    player = models.ForeignKey('Player', on_delete=models.CASCADE)
    tournament = models.ForeignKey('Tournament', on_delete=models.CASCADE)
    score = models.IntegerField()

    class Meta:
        ordering = ('tournament', 'order')

# Each tournament has its own ordering
tournament1_rank1 = TournamentRanking.objects.create(tournament=tournament1, player=player1)  # order=0
tournament1_rank2 = TournamentRanking.objects.create(tournament=tournament1, player=player2)  # order=1
tournament2_rank1 = TournamentRanking.objects.create(tournament=tournament2, player=player3)  # order=0
```

### Manual Reordering

```python
# Move an item to a specific position
third.order = 0
third.save()

# Original order: [first(0), second(1), third(2)]
# New order:      [third(0), first(1), second(2)]

# Move to end (any large number works)
first.order = 99
first.save()

# New order: [third(0), second(1), first(2)]
```

### Handling Deletions

```python
# Items are automatically reordered when one is deleted
second.delete()

# Original order: [third(0), second(1), first(2)]
# New order:      [third(0), first(1)]
```

### Creating at Specific Position

```python
# Insert at specific position
new_item = Playlist.objects.create(
    name="New Song",
    song=song4,
    order=1  # Insert at position 1
)

# Original order: [third(0), first(1)]
# New order:      [third(0), new_item(1), first(2)]
```

## Technical Details

### Automatic Reordering

The model maintains a continuous sequence by:
1. Handling new items (append or insert)
2. Reordering on deletions
3. Managing manual position changes

```python
def assert_order(sender, instance, **kwargs):
    order = getattr(instance, instance.order_field_name)
    group = list(instance.get_ordering_queryset().exclude(id=instance.pk))
    
    if order is not None:
        group.insert(max(0, order), instance)
    else:
        group.append(instance)
        
    for index, obj in enumerate(group):
        if obj.order != index:
            obj.__class__.objects.filter(pk=obj.pk).update(order=index)
```

### Meta Configuration

```python
class Meta:
    abstract = True
    ordering = ('order', '-updated_at')
    indexes = [
        models.Index(fields=['order']),
    ]
```

## Best Practices

1. Use OrderedModel when you need to maintain a specific sequence
2. Let the order field be managed automatically when possible
3. Use group-based ordering for separate sequences (e.g., by category, year)
4. Consider performance implications when reordering large sets
5. Use the built-in ordering in queries instead of manual sorting
6. Remember that order values are zero-based
7. Use database transactions when reordering multiple items