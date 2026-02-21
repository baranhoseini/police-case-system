from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    email = models.EmailField(unique=True)

    # TEMP (for migration only)
    phone = models.CharField(max_length=20, unique=True, null=True, blank=True)
    national_id = models.CharField(max_length=20, unique=True, null=True, blank=True)

    def __str__(self):
        return self.username