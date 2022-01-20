# Model Combinations

DRF Toolkit provides several pre-built model combinations for common use cases, as well as the ability to create custom combinations of model features.

## Available Combinations

### SoftDeleteInheritanceModel

Combines soft deletion with inheritance tracking:

```python
from drf_kit.models import SoftDeleteInheritanceModel

class Character(SoftDeleteInheritanceModel):
    name = models.CharField(max_length=100)

class Wizard(Character):
    magic_power = models.IntegerField()

class Warrior(Character):
    strength = models.IntegerField()

# Creates a wizard with type tracking
wizard = Wizard.objects.create(name="Merlin", magic_power=100)
print(wizard.type)  # "wizard"

# Soft deletes the wizard
wizard.delete()
print(wizard.is_deleted)  # True

# Query includes type information
Character.objects.filter(type="wizard")  # Excludes deleted
Character.objects.all_with_deleted().filter(type="wizard")  # Includes deleted
```

### SoftDeleteAvailabilityModel

Combines soft deletion with time-based availability:

```python
from drf_kit.models import SoftDeleteAvailabilityModel

class Event(SoftDeleteAvailabilityModel):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)

# Create an event with availability
event = Event.objects.create(
    name="Magic Show",
    starts_at=timezone.now(),
    ends_at=timezone.now() + timedelta(hours=2)
)

# Check availability
print(event.is_current)  # True if within time range
print(event.is_deleted)  # False

# Soft delete
event.delete()
print(event.is_deleted)  # True

# Queries respect both deletion and availability
Event.objects.current()  # Active and current events
Event.objects.all_with_deleted().future()  # All future events, including deleted
```

### SoftDeleteInheritanceOrderedModel

Combines soft deletion, inheritance tracking, and ordering:

```python
from drf_kit.models import SoftDeleteInheritanceOrderedModel

class Spell(SoftDeleteInheritanceOrderedModel):
    name = models.CharField(max_length=100)

class AttackSpell(Spell):
    damage = models.IntegerField()

class DefenseSpell(Spell):
    shield = models.IntegerField()

# Creates spells with automatic ordering
attack1 = AttackSpell.objects.create(name="Fireball", damage=100)  # order=0
attack2 = AttackSpell.objects.create(name="Lightning", damage=80)  # order=1
defense1 = DefenseSpell.objects.create(name="Shield", shield=50)   # order=0

# Ordering is maintained per type
print(attack1.order)  # 0
print(attack2.order)  # 1
print(defense1.order) # 0

# Soft delete maintains order
attack1.delete()
new_attack = AttackSpell.objects.create(name="Ice", damage=90)  # order=1
print(attack2.order)  # 0 (reordered)
```

## Creating Custom Combinations

You can create custom combinations by inheriting from multiple mixins:

```python
from drf_kit.models import (
    BaseModel,
    SoftDeleteModelMixin,
    OrderedModelMixin,
    AvailabilityModelMixin
)

class CustomModel(
    SoftDeleteModelMixin,
    OrderedModelMixin,
    AvailabilityModelMixin,
    BaseModel
):
    class Meta:
        abstract = True
        ordering = ('order', '-updated_at')
        indexes = (
            SoftDeleteModelMixin.Meta.indexes +
            OrderedModelMixin.Meta.indexes +
            AvailabilityModelMixin.Meta.indexes +
            BaseModel.Meta.indexes
        )
```

## Best Practices

1. Use pre-built combinations when they match your needs
2. When creating custom combinations:
   - Always include BaseModel last
   - Combine Meta classes properly
   - Merge indexes from all mixins
   - Consider the order of mixins (affects method resolution)
3. Test combined functionality thoroughly
4. Document the features provided by your combinations
5. Consider performance implications of multiple features
6. Use the most specific combination that meets your needs

## Feature Matrix

| Model Type | Soft Delete | Inheritance | Ordered | Availability |
|------------|-------------|-------------|---------|--------------|
| SoftDeleteInheritanceModel | ✓ | ✓ | | |
| SoftDeleteAvailabilityModel | ✓ | | | ✓ |
| SoftDeleteInheritanceOrderedModel | ✓ | ✓ | ✓ | |
| SoftDeleteOrderedModel | ✓ | | ✓ | |
| InheritanceOrderedModel | | ✓ | ✓ | |

## Technical Considerations

### Method Resolution Order

When combining models, be aware of Python's method resolution order (MRO):

```python
class CustomModel(SoftDeleteModelMixin, OrderedModelMixin, BaseModel):
    pass

print(CustomModel.__mro__)
# Shows the order in which methods are resolved
```
