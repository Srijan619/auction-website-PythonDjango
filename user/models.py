from django.db import models

class Account(models.Model):

    username=models.CharField(max_length=20)
    password=models.CharField(max_length=256)
    email= models.CharField(max_length=100)
