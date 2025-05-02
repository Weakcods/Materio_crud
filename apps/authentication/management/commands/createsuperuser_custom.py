from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser with predefined credentials'

    def handle(self, *args, **kwargs):
        User = get_user_model()
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='joshua',
                email='bacayjhoshuajm@gmail.com',
                password='bacay123',
                is_active=True,
                is_staff=True,
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully. Use username: admin, password: admin123'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists'))
