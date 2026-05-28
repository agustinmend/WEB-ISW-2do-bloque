from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from conference.models import UserAccount, Conference, Track, Session, Registration

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if Session.objects.exists():
            self.stdout.write(self.style.SUCCESS('La base de datos ya contiene datos. Saltando seeding.'))
            return

        users_to_create = [UserAccount(name=f"User {i}", email=f"user{i}@example.com") for i in range(500)]
        UserAccount.objects.bulk_create(users_to_create)
        users = list(UserAccount.objects.all())

        conf = Conference.objects.create(
            name="Symposium 2026",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=3),
            location="Centro de Convenciones"
        )
        track = Track.objects.create(name="Ingeniería de Software", conference=conf)

        sessions_to_create = []
        for i in range(300):
            sessions_to_create.append(Session(
                track=track,
                title=f"Arquitectura y Diseño - Sesión {i}",
                start_time=timezone.now() + timedelta(hours=i),
                end_time=timezone.now() + timedelta(hours=i, minutes=45),
                capacity=600,
                room=f"Sala {i % 10}"
            ))
        Session.objects.bulk_create(sessions_to_create)
        sessions = list(Session.objects.all())

        registrations_to_create = []
        for session in sessions:
            for user in users:
                registrations_to_create.append(Registration(session=session, user=user))
            
            if len(registrations_to_create) >= 10000:
                Registration.objects.bulk_create(registrations_to_create)
                registrations_to_create = []

        if registrations_to_create:
            Registration.objects.bulk_create(registrations_to_create)

        self.stdout.write(self.style.SUCCESS('Seeding completado exitosamente.'))