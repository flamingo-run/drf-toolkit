import logging

from django.core.cache import cache

logger = logging.getLogger(__name__)


class NotifyMinisterOfMagicTask:
    def run(self, *args, **kwargs):
        logger.info("Points to Griffindor!")


class LockableTask:
    def run(self):
        with cache.lock("triwizard", timeout=42):
            logger.info("The goblet of fire is mine.")
