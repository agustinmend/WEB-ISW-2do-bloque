from django.contrib import admin
from .models import UserAccount, Conference, Track, Speaker, Session, SessionSpeaker, Registration

class TrackInline(admin.TabularInline):
    model = Track
    extra = 1

class SessionInline(admin.TabularInline):
    model = Session
    extra = 1

class SessionSpeakerInline(admin.TabularInline):
    model = SessionSpeaker
    extra = 1

@admin.register(UserAccount)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

@admin.register(Conference)
class ConferenceAdmin(admin.ModelAdmin):
    list_display = ('name', 'start_date', 'end_date', 'location')
    search_fields = ('name', 'location')
    list_filter = ('start_date',)
    inlines = [TrackInline]

@admin.register(Track)
class TrackAdmin(admin.ModelAdmin):
    list_display = ('name', 'conference')
    search_fields = ('name', 'conference__name')
    list_filter = ('conference',)
    inlines = [SessionInline]

@admin.register(Speaker)
class SpeakerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email')
    search_fields = ('name', 'email')

@admin.register(Session)
class SessionAdmin(admin.ModelAdmin):
    list_display = ('title', 'track', 'start_time', 'end_time', 'capacity', 'room')
    search_fields = ('title', 'room')
    list_filter = ('track__conference', 'track')
    inlines = [SessionSpeakerInline]

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('user', 'session')
    search_fields = ('user__email', 'user__name')
    list_filter = ('session',)