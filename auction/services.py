from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from django.shortcuts import get_object_or_404

from auction.models import Auction
from auction.serializers import AucSerializer

class BrowseAuctionApi(APIView):
    def get(self,request):
     auctions = Auction.objects.all()
     serializer = AucSerializer(auctions, many=True)
     return Response(serializer.data)


class SearchAuctionApi(APIView):
    def get(self, request):
        auctions = Auction.objects.all()
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data)


class SearchAuctionWithTermApi(APIView):
    def get(self, request):
        term=request.GET["term"]
        auctions = Auction.objects.filter(title__icontains=term, status="Active").order_by('-created_date')
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data)


class SearchAuctionApiById(APIView):
    def get(self, request,id):
        term = request.GET["Id"]
        auctions = Auction.objects.filter(title__icontains=term, status="Active").order_by('-created_date')
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data)


class BidAuctionApi(APIView):
    pass
