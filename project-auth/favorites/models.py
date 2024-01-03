from django.contrib.postgres.fields import ArrayField
from django.db import models


class Favorites(models.Model):
    favorites_id = models.CharField(max_length=50, unique=True)
    saved_laptops = ArrayField(models.CharField(max_length=10, blank=True))
    updated_at = models.DateTimeField(auto_now=True)
