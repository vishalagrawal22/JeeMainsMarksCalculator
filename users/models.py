from django.db import models


# Create your models here.
class User(models.Model):
    email = models.CharField(max_length=100)
    password = models.CharField(max_length=100)
    is_verified = models.BooleanField(default=False)



