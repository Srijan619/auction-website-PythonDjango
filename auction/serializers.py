from rest_framework import serializers
from auction.models import Auction


class AucSerializer(serializers.ModelSerializer):

    class Meta:
        model = Auction
        fields = '__all__'


