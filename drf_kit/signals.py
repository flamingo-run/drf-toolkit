import logging

from django.dispatch import Signal

logger = logging.getLogger(__name__)


class UnplugSignal:
    """Temporarily disconnect a model from a signal"""

    def __init__(self, signal, func, model, dispatch_uid=None):
        self.signal = signal
        self.receiver = func
        self.sender = model
        self.dispatch_uid = dispatch_uid

    def start(self):
        self.signal.disconnect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
        )

    def __enter__(self):
        self.start()

    def stop(self):
        self.signal.connect(
            receiver=self.receiver,
            sender=self.sender,
            dispatch_uid=self.dispatch_uid,
            weak=False,
        )

    def __exit__(self, *args, **kwargs):
        self.stop()


pre_soft_delete = Signal(providing_args=["instance"])
post_soft_delete = Signal(providing_args=["instance"])
pre_undelete = Signal(providing_args=["instance"])
post_undelete = Signal(providing_args=["instance"])
