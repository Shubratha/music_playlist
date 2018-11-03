from rest_framework import serializers
from project_playlist.models import Playlist,Song
from django.contrib.auth.models import User

class SongSerializer(serializers.ModelSerializer):
    # playlist= serializers.StringRelatedField()
    # playlist = serializers.RelatedField(source='playlist.name', read_only=True)
    # playlist = serializers.PrimaryKeyRelatedField(queryset=Playlist.objects.all())
    class Meta:
        model = Song
        # fields = ('id','playlist','url','name')
        fields = ('id','playlist','url','name')

class PlaylistSerializer(serializers.ModelSerializer):
    # songs = serializers.StringRelatedField(many=True)
    # songs = SongSerializer(many = True)
    songs = SongSerializer(many=True)
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model= Playlist
        fields = ('id','user','name','songs')
        depth =1

    def create(self, validated_data):
        songs_data = validated_data.pop('songs')
        playlist = Playlist.objects.create(**validated_data)
        for song_data in songs_data:
            Song.objects.create(playlist=playlist, **song_data)
        return playlist

class UserSerializer(serializers.ModelSerializer):
    # playlist = serializers.RelatedField(source='playlist.name', read_only=True)
    playlists = PlaylistSerializer(many=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'playlists')
        depth = 2
        
    def create(self, validated_data):
        # import pdb; pdb.set_trace()
        playlists_data = validated_data.pop('playlists')
        user = User.objects.create(**validated_data)
        for playlist_data in playlists_data:
            Playlist.objects.create(user=user, **playlist_data)
        return user