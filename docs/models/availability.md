# Availability Models

The Availability Models in DRF Toolkit provide functionality for managing time-based availability of objects through a specialized manager. This is particularly useful for scenarios where you need to track when something is available, such as room bookings, event schedules, or time-limited resources.

## Features

- Specialized manager for time-based queries (past, current, future)
- Point-in-time availability checking with timezone support
- Comprehensive overlap detection for scheduling conflicts
- Support for open-ended ranges (null start/end dates)
- Efficient query methods for common availability patterns
- Automatic validation of date ranges
- Built-in timezone handling

## Models

### AvailabilityModel

The base model for time-based availability tracking.

```python
from drf_kit.models import AvailabilityModel

class RoomBooking(AvailabilityModel):
    room_number = models.CharField(max_length=100)
    description = models.TextField()
```

### Fields

- `starts_at` (DateTimeField, optional): When the availability period starts
- `ends_at` (DateTimeField, optional): When the availability period ends

Both fields can be null, allowing for open-ended ranges:
- If both are null: Always available
- If only starts_at is null: Available until ends_at
- If only ends_at is null: Available from starts_at onwards
- If both are set: Available during the specified period

## Model Properties

The AvailabilityModel provides properties to check its current state:

- `is_past`: True if the availability period has ended
- `is_current`: True if currently available
- `is_future`: True if the availability period hasn't started yet

These properties automatically handle timezone-aware comparisons and null values appropriately.

## Query Methods

The AvailabilityManager provides specialized methods for querying objects based on their availability state:

### Time-based Queries

```python
# Get past availabilities (ended before now)
RoomBooking.objects.past()

# Get current availabilities (active now)
RoomBooking.objects.current()

# Get future availabilities (starts after now)
RoomBooking.objects.future()

# Query with specific datetime
specific_date = timezone.now() + timedelta(days=7)
RoomBooking.objects.current(at=specific_date)
```

### Overlap Detection

The manager provides a powerful method to find objects with overlapping availability periods:

```python
# Find bookings that overlap with a given period
booking = RoomBooking(
    starts_at=timezone.now(),
    ends_at=timezone.now() + timedelta(hours=2)
)
overlapping = RoomBooking.objects.same_availability_of(booking)

# Handles various overlap scenarios:
# - Complete overlap (one range contains another)
# - Partial overlap (ranges intersect)
# - Open-ended ranges (null starts_at or ends_at)
```

The `same_availability_of` method is particularly useful for:
- Checking for scheduling conflicts
- Finding concurrent availabilities
- Validating time slot availability

## Validation

The model automatically validates that `ends_at` is after `starts_at` when both are provided:

```python
# This will raise IntegrityError
booking = RoomBooking.objects.create(
    starts_at=timezone.now(),
    ends_at=timezone.now() - timedelta(days=1)
)
```

## Usage Examples

### Basic Usage

```python
from django.utils import timezone
from datetime import timedelta

# Create a booking for tomorrow
tomorrow = timezone.now() + timedelta(days=1)
booking = RoomBooking.objects.create(
    room_number="101",
    starts_at=tomorrow,
    ends_at=tomorrow + timedelta(hours=2)
)

# Check availability state
booking.is_future  # True
booking.is_current  # False
booking.is_past  # False
```

### Open-ended Ranges

```python
# Always available
RoomBooking.objects.create(
    room_number="102",
    starts_at=None,
    ends_at=None
)

# Available until a specific time
RoomBooking.objects.create(
    room_number="103",
    starts_at=None,
    ends_at=timezone.now() + timedelta(days=30)
)

# Available from a specific time onwards
RoomBooking.objects.create(
    room_number="104",
    starts_at=timezone.now(),
    ends_at=None
)
```

### Conflict Detection

```python
# Check if a new booking conflicts with existing ones
new_booking = RoomBooking(
    room_number="101",
    starts_at=timezone.now(),
    ends_at=timezone.now() + timedelta(hours=1)
)

conflicts = RoomBooking.objects.same_availability_of(new_booking)
if conflicts.exists():
    print("This time slot is already booked!")
```

## Best Practices

1. Always use timezone-aware datetime objects
2. Consider using open-ended ranges for permanent or indefinite availability
3. Use `same_availability_of` for conflict detection instead of manual comparisons
4. Leverage manager methods (`current()`, `past()`, `future()`) for time-based filtering
5. Use the `at` parameter for point-in-time availability checks
6. Remember that null values in `starts_at` or `ends_at` represent open-ended ranges
7. Consider implementing business logic around overlapping availabilities
