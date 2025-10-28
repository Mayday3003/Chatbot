from django.core.management.base import BaseCommand
from apps.users.models import User
from apps.chatbot.models import KnowledgeEntry
from apps.tickets.models import Ticket

class Command(BaseCommand):
    help = 'Seed initial data for development'

    def handle(self, *args, **options):
        if not User.objects.filter(email='admin@example.com').exists():
            User.objects.create_superuser(email='admin@example.com', password='admin', username='admin')
            self.stdout.write(self.style.SUCCESS('Created admin user'))
        if not User.objects.filter(email='user@example.com').exists():
            User.objects.create_user(email='user@example.com', password='user', username='user')
            self.stdout.write(self.style.SUCCESS('Created regular user'))

        if KnowledgeEntry.objects.count() == 0:
            KnowledgeEntry.objects.create(title='Password reset', problem_description='Olvidé mi contraseña', solution_text='Sigue estos pasos para resetear la contraseña...')
            KnowledgeEntry.objects.create(title='VPN access', problem_description='No puedo conectar a VPN', solution_text='Verifica tu configuración y credenciales de VPN...')
            self.stdout.write(self.style.SUCCESS('Created KB entries'))

        if Ticket.objects.count() == 0:
            Ticket.objects.create(creador=User.objects.filter(email='user@example.com').first(), asunto='Problema de ejemplo')
            self.stdout.write(self.style.SUCCESS('Created sample ticket'))

        self.stdout.write(self.style.SUCCESS('Seed complete'))
