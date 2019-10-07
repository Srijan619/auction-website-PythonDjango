from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer

from django.shortcuts import get_object_or_404

from auction.models import Auction
from auction.serializers import AucSerializer


@api_view(['GET'])
@renderer_classes([JSONRenderer, ])
def auction_list(request):
    auctions = Auction.objects.all()
    serializer = AucSerializer(auctions, many=True)
    return Response(serializer.data)
