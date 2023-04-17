#!/usr/bin/env python
import os
import sys
from pathlib import Path

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "settings")
    os.environ.setdefault("APP_NAME", "test-app-dev")
    PROJECT_DIR = Path(__file__).parent.parent
    sys.path.insert(0, str(PROJECT_DIR))

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
