# Inheritance Models

The Inheritance Models in DRF Toolkit provide enhanced support for Django's model inheritance by automatically tracking model types and providing proper querying capabilities.

## InheritanceModel

The `InheritanceModel` is designed to work with Django's multi-table inheritance, automatically tracking the concrete model type for each instance.

```python
from drf_kit.models import InheritanceModel

class Tale(InheritanceModel):
    title = models.CharField(max_length=100)
    description = models.TextField()

class DarkTale(Tale):
    dark_level = models.IntegerField()

class HappyTale(Tale):
    happiness_level = models.IntegerField()
```

### Features

- Automatic type tracking
- Type field for model identification
- Seamless integration with Django's ORM
- Compatible with other mixins
- Pre-save signal handling

### Type Tracking

The model automatically maintains a `type` field that stores the concrete model class name:

```python
# Creating instances
tale = Tale.objects.create(title="Generic Tale")
dark_tale = DarkTale.objects.create(title="Dark Story", dark_level=666)
happy_tale = HappyTale.objects.create(title="Happy Story", happiness_level=100)

# Type field is automatically set
print(tale.type)  # "tale"
print(dark_tale.type)  # "darktale"
print(happy_tale.type)  # "happytale"
```

### Querying

You can query through the parent model to get all instances, including child models:

```python
# Get all tales (including DarkTale and HappyTale instances)
all_tales = Tale.objects.all()

# Filter specific types
dark_tales = Tale.objects.filter(type="darktale")
happy_tales = Tale.objects.filter(type="happytale")
```

## Usage Examples

### Basic Inheritance

```python
from drf_kit.models import InheritanceModel

class Spell(InheritanceModel):
    name = models.CharField(max_length=100)
    power = models.IntegerField()

class CombatSpell(Spell):
    damage = models.IntegerField()

class HealingSpell(Spell):
    healing_power = models.IntegerField()

# Create instances
combat_spell = CombatSpell.objects.create(
    name="Fireball",
    power=50,
    damage=100
)

healing_spell = HealingSpell.objects.create(
    name="Heal",
    power=30,
    healing_power=75
)

# Query through parent
all_spells = Spell.objects.all()
```

### Combining with Other Mixins

The inheritance model works seamlessly with other mixins:

```python
from drf_kit.models import SoftDeleteInheritanceModel

class Character(SoftDeleteInheritanceModel):
    name = models.CharField(max_length=100)

class Wizard(Character):
    magic_power = models.IntegerField()

class Warrior(Character):
    strength = models.IntegerField()

# Supports both inheritance and soft delete
wizard = Wizard.objects.create(name="Merlin", magic_power=100)
wizard.delete()  # Soft delete
```

### Type-Based Logic

```python
class SpellEffect:
    def apply(self, spell):
        if spell.type == "combatspell":
            self.apply_combat_effect(spell)
        elif spell.type == "healingspell":
            self.apply_healing_effect(spell)
```

## Technical Details

### Type Field

```python
class InheritanceModelMixin(models.Model):
    type = models.CharField(max_length=100)
    
    class Meta:
        abstract = True
```

### Automatic Type Setting

The type is automatically set through a pre-save signal:

```python
def assert_inherited_type(sender, instance, **kwargs):
    instance.type = instance.__class__.__name__.lower()

@classmethod
def __init_subclass__(cls, **kwargs):
    super().__init_subclass__(**kwargs)
    pre_save.connect(assert_inherited_type, cls)
```

## Best Practices

1. Use InheritanceModel for multi-table inheritance scenarios
2. Let the type field be managed automatically
3. Query through the parent model when you need all subtypes
4. Combine with other mixins as needed (e.g., SoftDeleteInheritanceModel)
5. Use the type field for type-specific logic rather than isinstance checks