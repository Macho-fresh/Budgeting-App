from django.db import models
from django.contrib.auth.models import AbstractUser

class User(models.Model):
    email = models.CharField(unique=True)
