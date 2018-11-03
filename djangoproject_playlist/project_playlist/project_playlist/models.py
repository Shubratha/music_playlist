from django.db import models
from django.contrib.auth.models import User

class Playlist(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE, default=1, related_name="playlists")
    name= models.CharField(max_length=200, default = 'name')

    def __str__(self):
        return self.name

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "songs": [s.to_dict() for s in self.song_set.all()]
        }


class Song(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name="songs")
    # playlist = models.ManyToManyField(Playlist)
    url = models.URLField()
    name = models.CharField(max_length=200, default="song")

    def embed_url(self):
        video_id = self.url.replace("https://www.youtube.com/watch?v=", "")
        return "http://www.youtube.com/embed/" + video_id

    def __str__(self):
        return "{} - {} - {}".format(self.playlist.name, self.url,self.name)

    def to_dict(self):
        return{
            "id":self.id,
            "url":self.url,
            "name":self.name,
        }