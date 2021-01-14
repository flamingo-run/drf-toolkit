#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
    os.environ.setdefault('APP_NAME', 'test-app-dev')
    PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, PROJECT_DIR)

    from django.core.management import execute_from_command_line

    execute_from_command_line(sys.argv)
