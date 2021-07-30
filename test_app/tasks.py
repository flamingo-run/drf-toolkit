from django.core.cache import cache


class NotifyMinisterOfMagicTask:
    def run(self, *args, **kwargs):
        print("Points to Griffindor!")


class LockableTask:
    def run(self):
        with cache.lock("triwizard", timeout=42):
            print("The goblet of fire is mine.")
