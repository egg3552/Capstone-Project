"""
Debug static files configuration for Heroku deployment issues.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.contrib.staticfiles.finders import get_finders


class Command(BaseCommand):
    help = 'Debug static files configuration and environment'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== Static Files Debug Info ==='))
        
        # Environment information
        self.stdout.write(f'Python version: {os.sys.version}')
        self.stdout.write(f'Django version: {settings.INSTALLED_APPS}')
        self.stdout.write(f'IS_HEROKU: {"DYNO" in os.environ}')
        self.stdout.write(f'DEBUG: {settings.DEBUG}')
        
        # Static files settings
        self.stdout.write('\n=== Static Files Settings ===')
        self.stdout.write(f'STATIC_URL: {settings.STATIC_URL}')
        self.stdout.write(f'STATIC_ROOT: {settings.STATIC_ROOT}')
        self.stdout.write(f'STATICFILES_DIRS: {settings.STATICFILES_DIRS}')
        
        # Storage backend
        self.stdout.write(f'\nStorage backend: {settings.STORAGES["staticfiles"]["BACKEND"]}')
        
        # Directory checks
        self.stdout.write('\n=== Directory Checks ===')
        self.stdout.write(f'BASE_DIR exists: {os.path.exists(settings.BASE_DIR)}')
        self.stdout.write(f'STATIC_ROOT exists: {os.path.exists(settings.STATIC_ROOT)}')
        
        for static_dir in settings.STATICFILES_DIRS:
            exists = os.path.exists(static_dir)
            self.stdout.write(f'Static dir {static_dir} exists: {exists}')
            if exists:
                files = os.listdir(static_dir)
                self.stdout.write(f'  Contents: {files}')
        
        # Finders information
        self.stdout.write('\n=== Static Files Finders ===')
        for finder in get_finders():
            self.stdout.write(f'Finder: {finder.__class__.__name__}')
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
                value = f'{value[:10]}...' if len(value) > 10 else value
            self.stdout.write(f'{var}: {value}')
        
        self.stdout.write(self.style.SUCCESS('\n=== Debug Complete ==='))