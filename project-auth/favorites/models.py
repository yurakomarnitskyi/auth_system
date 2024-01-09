from django.contrib.postgres.fields import ArrayField
from django.db import models


class Favorites(models.Model):
    """
    A Django model representing a user's list of favorite laptops.

    Attributes:
        favorites_id (CharField): A unique identifier for the user's favorites list. Can be whether User primary key or
        unique generated id for unauthorized user.
        saved_laptops (ArrayField): An array of strings, each representing a laptop ID that the user has marked
        as favorite.
        updated_at (DateTimeField): A timestamp indicating the last time the favorites list was updated.
    """
    favorites_id = models.CharField(max_length=50, unique=True)
    saved_laptops = ArrayField(models.CharField(max_length=24, blank=True))
    updated_at = models.DateTimeField(auto_now=True)
