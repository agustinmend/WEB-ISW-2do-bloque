from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from conference.models import UserAccount, Conference, Track, Session, Registration, Speaker
import uuid
import random

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        if Session.objects.exists():
            self.stdout.write(self.style.SUCCESS('La base de datos ya contiene datos. Saltando seeding.'))
            return

        users_to_create = [UserAccount(id=uuid.uuid4(), name=f"User {i}", email=f"user{i}@example.com") for i in range(500)]
        UserAccount.objects.bulk_create(users_to_create)
        users = list(UserAccount.objects.all())

        conf = Conference.objects.create(
            name="Symposium 2026",
            start_date=timezone.now(),
            end_date=timezone.now() + timedelta(days=3),
            location="Centro de Convenciones"
        )
        track = Track.objects.create(name="Ingeniería de Software", conference=conf)

        speakers_to_create = [
            Speaker(id=uuid.uuid4(), name=f"Dr. Ponente {i}", email=f"ponente{i}@ejemplo.com") 
            for i in range(15)
        ]
        Speaker.objects.bulk_create(speakers_to_create)
        speakers = list(Speaker.objects.all())

        sessions_to_create = []
        for i in range(300):
            sessions_to_create.append(Session(
                id=uuid.uuid4(),
                track=track,
                title=f"Arquitectura y Diseño - Sesión {i}",
                start_time=timezone.now() + timedelta(hours=i),
                end_time=timezone.now() + timedelta(hours=i, minutes=45),
                capacity=600,
                room=f"Sala {i % 10}"
            ))
        Session.objects.bulk_create(sessions_to_create)
        sessions = list(Session.objects.all())

        SessionSpeaker = Session.speakers.through
        session_speakers_to_create = []
        
        for session in sessions:
            assigned_speakers = random.sample(speakers, k=random.randint(1, 2))
            for speaker in assigned_speakers:
                session_speakers_to_create.append(
                    SessionSpeaker(session_id=session.id, speaker_id=speaker.id)
                )
        
        SessionSpeaker.objects.bulk_create(session_speakers_to_create)

        registrations_to_create = []
        for session in sessions:
            for user in users:
                registrations_to_create.append(Registration(id=uuid.uuid4(), session=session, user=user))
            
            if len(registrations_to_create) >= 10000:
                Registration.objects.bulk_create(registrations_to_create)
                registrations_to_create = []

        if registrations_to_create:
            Registration.objects.bulk_create(registrations_to_create)

        self.stdout.write(self.style.SUCCESS(
            f'Seeding completado exitosamente: 500 Usuarios, 15 Speakers, 300 Sesiones, {len(session_speakers_to_create)} vínculos M2M.'
        ))