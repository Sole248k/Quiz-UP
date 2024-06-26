from django.db import models


class Users(models.Model):
    username = models.CharField(max_length=30)
    email = models.EmailField(max_length=30)
    password = models.CharField(max_length=16)
    about_user = models.TextField(default='')
