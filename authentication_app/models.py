from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    custom = models.CharField(max_length=1000, null=True, blank=True)
