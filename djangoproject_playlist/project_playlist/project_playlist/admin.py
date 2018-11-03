from django.contrib import admin
from .models import Playlist,Song

class SongInline(admin.TabularInline):
    model = Song

class PlaylistAdmin(admin.ModelAdmin):
    model=Playlist
    inlines=[SongInline]

admin.site.register(Playlist, PlaylistAdmin)