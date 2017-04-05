from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        admin_email = 'admin@hello-sales.com'
        admin_password = '1q2w3e4r'

        if not User.objects.filter(email=admin_email).exists():
            User.objects.create_superuser(admin_email, admin_password)
