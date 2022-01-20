# Signals

DRF Toolkit provides a way to temporarily disable Django signals using the `UnplugSignal` context manager.

## UnplugSignal

The `UnplugSignal` class allows you to temporarily disconnect a specific signal from a model. This is particularly useful in testing scenarios or when you need to perform operations without triggering certain signals.

### Usage

```python
from django.db.models.signals import post_save
from drf_kit.signals import UnplugSignal

# Create an UnplugSignal instance
unplugged = UnplugSignal(
    signal=post_save,              # The Django signal to disconnect
    func=my_signal_handler,        # The signal handler function
    model=MyModel,                 # The sender model
    dispatch_uid=None              # Optional dispatch_uid if used in signal connection
)

# Use as a context manager
with unplugged:
    # Inside this block, the signal is disconnected
    instance.save()  # This won't trigger the signal

# After the block, the signal is automatically reconnected
instance.save()  # This will trigger the signal
```

### Example

Here's a practical example showing how to use `UnplugSignal` in a test case:

```python
from django.db.models.signals import post_save
from drf_kit.signals import UnplugSignal

def test_signal_handling():
    # Create an instance that would normally trigger a signal
    instance = MyModel.objects.create()  # Signal is triggered

    # Temporarily disable the signal
    with UnplugSignal(
        signal=post_save,
        func=notification_handler,
        model=MyModel
    ):
        instance.status = 'updated'
        instance.save()  # Signal is not triggered

    instance.status = 'final'
    instance.save()  # Signal is triggered again
```

The signal is automatically reconnected when exiting the context manager, ensuring that your signal handling returns to normal operation after the required temporary disconnection.
