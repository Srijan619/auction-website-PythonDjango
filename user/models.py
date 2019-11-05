from django.db import models
from django.contrib.auth.models import User

class UserLanguage(models.Model):
    user=models.ForeignKey(User,blank=True,null=True,on_delete=models.CASCADE)
    language =models.CharField(max_length=45,null=True, default="en")

    def __str__(self):
        return self.language