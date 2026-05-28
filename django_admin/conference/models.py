import uuid
from django.db import models
from django.utils import timezone

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(default=timezone.now)
    modified = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class UserAccount(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)

    class Meta:
        db_table = '"content"."user_account"'
        verbose_name = 'User Account'
        verbose_name_plural = 'User Accounts'

    def __str__(self):
        return self.name

class Conference(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = '"content"."conference"'
        verbose_name = 'Conference'
        verbose_name_plural = 'Conferences'

    def __str__(self):
        return self.name

class Track(BaseModel):
    conference = models.ForeignKey(Conference, on_delete=models.CASCADE, related_name='tracks')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)

    class Meta:
        db_table = '"content"."track"'
        verbose_name = 'Track'
        verbose_name_plural = 'Tracks'

    def __str__(self):
        return self.name

class Session(BaseModel):
    track = models.ForeignKey(Track, on_delete=models.CASCADE, related_name='sessions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    capacity = models.IntegerField()
    room = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        db_table = '"content"."session"'
        verbose_name = 'Session'
        verbose_name_plural = 'Sessions'

    def __str__(self):
        return self.title

class Speaker(BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    
    sessions = models.ManyToManyField(Session, through='SessionSpeaker', related_name='speakers')

    class Meta:
        db_table = '"content"."speaker"'
        verbose_name = 'Speaker'
        verbose_name_plural = 'Speakers'

    def __str__(self):
        return self.name

class SessionSpeaker(BaseModel):
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    speaker = models.ForeignKey(Speaker, on_delete=models.CASCADE)

    class Meta:
        db_table = '"content"."session_speaker"'
        unique_together = ('session', 'speaker')
        verbose_name = 'Session Speaker'
        verbose_name_plural = 'Session Speakers'

class Registration(BaseModel):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE, related_name='registrations')
    session = models.ForeignKey(Session, on_delete=models.CASCADE, related_name='registrations')

    class Meta:
        db_table = '"content"."registration"'
        unique_together = ('session', 'user')
        verbose_name = 'Registration'
        verbose_name_plural = 'Registrations'