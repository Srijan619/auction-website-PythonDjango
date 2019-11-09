import uuid as uuid
from django.db import models


class Auction(models.Model):
    uuid = models.UUIDField(primary_key=False, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=45)
    description = models.CharField(max_length=45)
    minimum_price = models.CharField(max_length=50,default=0.0)
    deadline_date = models.DateTimeField()
    created_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=500, default="Active")
    hosted_by = models.CharField(max_length=45, default="")
    version = models.IntegerField(default=0)


    def __str__(self):
        return self.title

class Bidding(models.Model):
    auction=models.ForeignKey(Auction,blank=True,null=True,on_delete=models.CASCADE,)
    new_price=models.CharField(max_length=50, default=0.0)
    hosted_by=models.CharField(max_length=45, default="")
    bidder= models.CharField(max_length=45, default="")
    bid_time=models.DateTimeField(auto_now_add=True)
    bid_version = models.IntegerField(default=0)

    def __str__(self):
        return self.new_price
