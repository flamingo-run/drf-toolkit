# Monkey patch until : https://github.com/chibisov/drf-extensions/issues/294
from django.core.exceptions import EmptyResultSet
from django.db.models.sql import datastructures

datastructures.EmptyResultSet = EmptyResultSet


# because we can't trust None, that could mean
# "not set yet" or "set as None:
UNSET = object()
