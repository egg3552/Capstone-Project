from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from blog.models import UserProfile


class Command(BaseCommand):
    help = 'Create a test admin user with admin permissions'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            default='testadmin',
            help='Username for the test admin (default: testadmin)'
        )
        parser.add_argument(
            '--email',
            type=str,
            default='testadmin@example.com',
            help='Email for the test admin (default: testadmin@example.com)'
        )
        parser.add_argument(
            '--password',
            type=str,
            default='TestAdmin123!',
            help='Password for the test admin (default: TestAdmin123!)'
        )

    def handle(self, *args, **options):
        username = options['username']
        email = options['email']
        password = options['password']

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'User "{username}" already exists!')
            )
            return

        try:
            # Create the user
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name='Test',
                last_name='Admin',
                is_staff=True,  # Django admin access
                is_superuser=True  # Full admin permissions
            )

            # Create or update UserProfile with admin role
            user_profile, created = UserProfile.objects.get_or_create(
                user=user,
                defaults={
                    'role': 'admin',
                    'bio': 'Test admin account for development and testing.',
                }
            )

            if not created:
                user_profile.role = 'admin'
                user_profile.bio = 'Test admin account for development.'
                user_profile.save()

            self.stdout.write(
                self.style.SUCCESS(
                    f'Successfully created test admin user: {username}'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Email: {email}'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    f'Password: {password}'
                )
            )
            self.stdout.write(
                self.style.SUCCESS(
                    'User has Django superuser and blog admin permissions.'
                )
            )

        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating test admin: {str(e)}')
            )