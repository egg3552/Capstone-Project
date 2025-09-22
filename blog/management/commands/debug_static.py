"""
Debug static files configuration for Heroku deployment issues.
"""
import os
import sys
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.staticfiles.finders import get_finders
import django


class Command(BaseCommand):
    help = 'Debug static files configuration and environment'

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('=== Static Files Debug Info ===')
        )

        # Environment information
        self.stdout.write(f'Python version: {sys.version.split()[0]}')
        self.stdout.write(f'Django version: {django.get_version()}')
        self.stdout.write(f'IS_HEROKU: {"DYNO" in os.environ}')
        self.stdout.write(f'DEBUG: {settings.DEBUG}')

        # Static files settings
        self.stdout.write('\n=== Static Files Settings ===')
        self.stdout.write(f'STATIC_URL: {settings.STATIC_URL}')
        self.stdout.write(f'STATIC_ROOT: {settings.STATIC_ROOT}')
        self.stdout.write(f'STATICFILES_DIRS: {settings.STATICFILES_DIRS}')

        # Storage backend
        backend = settings.STORAGES["staticfiles"]["BACKEND"]
        self.stdout.write(f'\nStorage backend: {backend}')

        # Directory checks
        self.stdout.write('\n=== Directory Checks ===')
        base_exists = os.path.exists(settings.BASE_DIR)
        self.stdout.write(f'BASE_DIR exists: {base_exists}')
        static_root_exists = os.path.exists(settings.STATIC_ROOT)
        self.stdout.write(f'STATIC_ROOT exists: {static_root_exists}')

        for static_dir in settings.STATICFILES_DIRS:
            exists = os.path.exists(static_dir)
            self.stdout.write(f'Static dir {static_dir} exists: {exists}')
            if exists:
                try:
                    files = os.listdir(static_dir)
                    self.stdout.write(f'  Contents: {files}')
                except Exception as e:
                    self.stdout.write(f'  Error reading directory: {e}')

        # Finders information
        self.stdout.write('\n=== Static Files Finders ===')
        for finder in get_finders():
            finder_name = finder.__class__.__name__
            self.stdout.write(f'Finder: {finder_name}')
            try:
                locations = list(finder.list([]))
                self.stdout.write(f'  Found {len(locations)} files')
            except Exception as e:
                self.stdout.write(f'  Error: {e}')

        # Environment variables
        self.stdout.write('\n=== Environment Variables ===')
        env_vars = ['DYNO', 'SECRET_KEY', 'DEBUG', 'ALLOWED_HOSTS']
        for var in env_vars:
            value = os.environ.get(var, 'NOT SET')
            if var == 'SECRET_KEY' and value != 'NOT SET':
                if len(value) > 10:
                    value = f'{value[:10]}...'
            self.stdout.write(f'{var}: {value}')

        self.stdout.write(
            self.style.SUCCESS('\n=== Debug Complete ===')
        )