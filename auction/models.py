from django.db import models


class Auction(models.Model):
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=45)
    minimum_price = models.CharField(max_length=50,default=0.0)
    deadline_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=500, default="Active")
    hosted_by = models.CharField(max_length=45, default="")


    def __str__(self):
        return self.title

