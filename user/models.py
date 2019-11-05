from django.db import models
from django.contrib.auth.models import User

class UserLanguage(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    language_code=models.CharField(max_length=45, default="en")
