from rest_framework.views import APIView
from rest_framework.decorators import api_view, renderer_classes, authentication_classes, permission_classes
from rest_framework.authentication import BasicAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from django.utils.translation import gettext as _
from django.core.mail import send_mail
from django.contrib.auth.models import User
from _datetime import datetime, timezone

from django.shortcuts import get_object_or_404

from auction.models import Auction, Bidding
from auction.serializers import AucSerializer, BidSerializer


class BrowseAuctionApi(APIView):
    def get(self, request):
        auctions = Auction.objects.filter(status="Active")
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data, status=200)


class SearchAuctionApi(APIView):
    def get(self, request, title):
        auctions = Auction.objects.filter(title__icontains=title, status="Active").order_by('-created_date')
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data, status=200)


class SearchAuctionWithTermApi(APIView):
    def get(self, request):
        term = request.GET["term"]
        auctions = Auction.objects.filter(title__icontains=term, status="Active").order_by('-created_date')
        serializer = AucSerializer(auctions, many=True)
        return Response(serializer.data, status=200)


class SearchAuctionApiById(APIView):
    def get(self, request, id):
        auctions = Auction.objects.get(id=id, status="Active")
        serializer = AucSerializer(auctions)
        return Response(serializer.data, status=200)


class BidAuctionApi(APIView):
    authentication_classes = [BasicAuthentication, ]
    permission_classes = [IsAuthenticated, ]

    def get(self, request, id):
        bid = Bidding.objects.filter(auction_id=id)
        serializer = BidSerializer(bid, many=True)
        return Response(serializer.data, status=200)

    def post(self, request, id):

        biddings = Bidding.objects.filter(auction_id=id).order_by('new_price').last()

        auction = Auction.objects.get(id=id)

        data = request.data
        serializer = BidSerializer(biddings, data=data)
        if auction.hosted_by == request.user.username:
            return Response({'message': "Cannot bid on own auction"}, status=400)
        elif auction.status == "Banned":
            return Response({'message': "Can only bid on active auction"}, status=400)
        elif (str(data["new_price"]).isdigit() == False):
            return Response({'message': "Bid must be a number"}, status=400)
        elif ((biddings is None and (float(auction.minimum_price)) >= float(data["new_price"])) or (
                biddings is not None and (float(biddings.new_price)) >= float(data["new_price"]))):
            return Response({'message': "New bid must be greater than the current bid at least 0.01"}, status=400)
        elif serializer.is_valid():
          #  data = {}

            # data['new_price'] = data
            # data['hosted_by'] = auction.hosted_by
            #  data['bidder'] = request.user.username
            # data['bid_time'] = datetime.now(timezone.utc)
            serializer.save()
            return Response({'message': "Bid successfully", 'title':auction.title,'current_price':data['new_price']}, status=200)

            ## Email to the bidder
            subject = _("Bid Successful")
            message = _("Thank you for bidding  an auction. You will be notified of the situation.")
            to_email = [request.user.email]

            send_mail(subject, message, 'no-reply@yaas.com', to_email, fail_silently=False)

            ## Email to the Host
            user = User.objects.get(username=auction.hosted_by)
            subject2 = _("New bidder")
            message2 = _("Hello, There was a new bid by " + request.user.username)
            to_email2 = [user.email]

            send_mail(subject2, message2, 'no-reply@yaas.com', to_email2, fail_silently=False)
        else:
            return Response(serializer.errors, status=400)

