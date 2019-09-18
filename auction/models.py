from django.db import models


class Auction(models.Model):
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=45)
    minimum_price = models.CharField(default=0.0)
    created_date = models.DateTimeField(auto_now_add=True)
    deadline_date = models.DateTimeField()
    status = models.CharField(max_length=500, default="Active")

