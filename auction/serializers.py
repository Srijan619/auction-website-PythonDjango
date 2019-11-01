from rest_framework import serializers
from auction.models import Auction, Bidding


class AucSerializer(serializers.ModelSerializer):

    class Meta:
        model = Auction
        fields = '__all__'

class BidSerializer(serializers.ModelSerializer):

    class Meta:
        model = Bidding
        fields = '__all__'



