from django.db import models
from django.utils import timezone

# Create your models here.
class SpotifyToken(models.Model):
    spotify_user_id = models.CharField(max_length=100, unique=True)
    access_token = models.CharField(max_length=255)
    refresh_token = models.CharField(max_length=255)
    token_type = models.CharField(max_length=50)
    expires_at = models.DateTimeField()
