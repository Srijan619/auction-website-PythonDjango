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
      auctions = Auction.objects.filter(status="Active")
      serializer = AucSerializer(auctions, many=True)
      return Response(serializer.data, status=200)


class SearchAuctionApi(APIView):
    def get(self, request,title):
        auctions = Auction.objects.filter(title__icontains=title, status="Active").order_by('-created_date')
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data, status=200)


class SearchAuctionWithTermApi(APIView):
    def get(self, request):
        term=request.GET["term"]
        auctions = Auction.objects.filter(title__icontains=term, status="Active").order_by('-created_date')
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data, status=200)


class SearchAuctionApiById(APIView):
    def get(self, request, id):
        auctions = Auction.objects.filter(id=id, status="Active").order_by('-created_date')
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data)


class BidAuctionApi(APIView):
    def get(self, request, id):
        pass
    def post(self,request, id):
        pass
