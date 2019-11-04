from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import Auction, Bidding
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from .forms import CreateAuctionForm, EditAuctionForm, Auction, BiddingForm
from django.utils.translation import gettext as _
from _datetime import datetime, timezone
from django.core.serializers.json import DjangoJSONEncoder
import requests
import json

url = 'https://api.exchangerate-api.com/v4/latest/EUR'


def index(request):
    auctions = Auction.objects.filter(status="Active").order_by('-created_date')
    return render(request, "home.html", {"auctions": auctions})


def search(request):
    if request.GET["term"] != "":  # term is just a reference to search check html for search
        criteria = request.GET["term"].strip()
        auctions = Auction.objects.filter(title__icontains=criteria, status="Active").order_by('-created_date')
    else:
        auctions = Auction.objects.filter(status="Active").order_by('-created_date')

    return render(request, "home.html", {'auctions': auctions})


@method_decorator(login_required, name="dispatch")
class CreateAuction(View):
    def get(self, request):
        form = CreateAuctionForm()
        return render(request, "create_auction.html", {"form": form})

    def post(self, request):
        form = CreateAuctionForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data

            deadline = cd.get("deadline_date")
            tday = datetime.now(timezone.utc)

            time_diff = deadline - tday
            hour = time_diff.total_seconds() / 3600.0
            print(hour)

            hosted_by = request.user.username
            if (hour >= 72):
                new_auction = Auction.objects.create(title=cd["title"], description=cd["description"],
                                                     minimum_price=cd["minimum_price"],
                                                     deadline_date=cd["deadline_date"], hosted_by=hosted_by)

                new_auction.save()
                subject = _("Auction created")
                message = _("Thank you for creating an auction. Below link provides to modify the auction details.")
                to_email = [request.user.email]

                send_mail(subject, message, 'no-reply@yaas.com', to_email, fail_silently=False)
                messages.info(request, _("Auction has been created successfully, check your emails"))
                return HttpResponseRedirect(reverse("auction:index"))
            else:
                messages.info(request, _("The deadline date should be at least 72 hours from now"))
                return render(request, "create_auction.html", {"form": form})


        else:
           
            return render(request, "create_auction.html", {"form": form})


@method_decorator(login_required, name="dispatch")
class EditAuction(View):

    def get(self, request, id):
        auction = Auction.objects.get(id=id)
        if auction.hosted_by == request.user.username:
            print(request.user.username)
            print(auction.id)
            form = EditAuctionForm()

            return render(request, "edit_auction.html", {"form": form})
        else:
            messages.info(request, "That is not your auction to edit")
            return HttpResponseRedirect(reverse("auction:index"))

    def post(self, request, id):
        auction = Auction.objects.get(id=id)
        if auction.hosted_by == request.user.username:
            form = EditAuctionForm(request.POST)
            if form.is_valid():
                cd = form.cleaned_data
                title = cd['title']
                description = cd['description']
                auction.description = description
                auction.title = title
                auction.save()
                messages.info(request, _("Auction has been updated successfully"))
                return HttpResponseRedirect(reverse("auction:index"))
            else:
                return render(request, "edit_auction.html", {"form": form})
        else:
            messages.info(request, _("That is not your auction"))
            return HttpResponseRedirect(reverse("auction:index"))


@method_decorator(login_required, name="dispatch")
class bid(View):
    def get(self, request, item_id):
        auction = Auction.objects.get(id=item_id)
        auctions = Auction.objects.filter(status="Active").order_by('-created_date')
        bidding_all = Bidding.objects.filter(auction_id=item_id).order_by('-new_price')
        biddings = Bidding.objects.filter(auction_id=item_id).order_by('new_price').last()

        delta = auction.deadline_date - datetime.now(timezone.utc)
        if auction.status == "Banned":
            messages.info(request, "You can only bid on active auction")
            return render(request, "home.html", {"auctions": auctions})
        elif auction.hosted_by == request.user.username:
            messages.info(request, "You cannot bid on your own auctions")
            return render(request, "home.html", {"auctions": auctions})
        elif delta.total_seconds() <= 0:
            messages.info(request, "You can only bid on active auction")
            return render(request, "home.html", {"auctions": auctions})
        else:
            form = BiddingForm()
            return render(request, "bid_auction.html",
                          {"form": form, "auction": auction, "biddings": biddings, "bidding_all": bidding_all})

    def post(self, request, item_id):
        auction = Auction.objects.get(id=item_id)
        auctions = Auction.objects.filter(status="Active").order_by('-created_date')
        biddings = Bidding.objects.filter(auction_id=item_id).order_by('new_price').last()
        bidding_all = Bidding.objects.filter(auction_id=item_id).order_by('-new_price')
        delta = auction.deadline_date - datetime.now(timezone.utc)
        form = BiddingForm(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            new_price = cd['new_price']
            if auction.status == "Banned":
                messages.info(request, "You can only bid on active auction")
                return render(request, "home.html", {"auctions": auctions})
            elif auction.hosted_by == request.user.username:
                messages.info(request, "You cannot bid on your own auctions")
                return render(request, "home.html", {"auctions": auctions})
            elif delta.total_seconds() <= 0:
                messages.info(request, "You can only bid on active auction")
                return render(request, "home.html", {"auctions": auctions})
            elif ((biddings is None and (float(auction.minimum_price)) < new_price) or (
                    biddings is not None and (float(biddings.new_price)) < new_price)):

                bids = Bidding.objects.create(new_price=new_price, hosted_by=auction.hosted_by,
                                              bidder=request.user.username, auction=auction)
                bids.save()

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

                messages.info(request, "You has bid successfully")
                return HttpResponseRedirect(reverse('auction:index'))
            else:
                messages.info(request, "New bid must be greater than the current bid for at least 0.01")
                return render(request, "bid_auction.html",
                              {"form": form, "auction": auction, "bidding_all": bidding_all, "biddings": biddings})

        else:
            return render(request, "bid_auction.html",
                          {"form": form, "auction": auction, "bidding_all": bidding_all, "biddings": biddings})


@login_required()
def ban(request, item_id):
    if request.user.is_superuser:
        auction = Auction.objects.get(id=item_id)
        biddings = Bidding.objects.filter(auction_id=item_id)
        auction.status = "Banned"
        auction.save()

        ## Email to the Host
        user = User.objects.get(username=auction.hosted_by)
        subject = _("Banned")
        message2 = _("Hello Host, Your auction was banned ")
        to_email2 = [user.email]
        send_mail(subject, message2, 'no-reply@yaas.com', to_email2, fail_silently=False)

        ## Email to the Bidders

        message = _("Hello bidders, The bidded auction was banned ")

        bidder = Bidding.objects.filter(auction_id=item_id)
        for bidders in bidder:
            emails = User.objects.filter(username=bidders.bidder)
            for email in emails:
                receipent_list = [email.email]
                send_mail(subject, message, 'no-reply@yaas.com', receipent_list, fail_silently=False)
        messages.info(request, "Ban successfully")
        return HttpResponseRedirect(reverse('auction:index'))
    else:
        messages.info(request, "You are not entitled to ban an auction.")
        return HttpResponseRedirect(reverse('auction:index'))


class bannedAuctions(View):
    def get(self, request):
        auctions = Auction.objects.filter(status="Banned").order_by('-created_date')
        return render(request, "banned_auctions.html", {"auctions": auctions})


def resolve(request):
    if request.method == "GET":
        auctions = Auction.objects.filter(status="Active")
        resolved_auction = Auction.objects.filter(status="Resolved")

        for auction in auctions:
            delta = auction.deadline_date - datetime.now(timezone.utc)
            if (delta.total_seconds() <= 0):
                auction.status = "Resolved"
                auction.save()

        for resolve_auction in resolved_auction:
            bidding = Bidding.objects.filter(auction_id=resolve_auction.id).order_by('new_price').last()

            ## Email to the Hosts
            user = User.objects.get(username=resolve_auction.hosted_by)
            subject = _("Resolved")
            message2 = _("Hello Hosts, Your auctions were resolved ")
            to_email2 = [user.email]
            send_mail(subject, message2, 'no-reply@yaas.com', to_email2, fail_silently=False)

            ## Email to the Bidders

            message = _("Hello bidders, The bidded auction was resolved ")

            bidder = Bidding.objects.filter(auction_id=resolve_auction.id)
            for bidders in bidder:
                emails = User.objects.filter(username=bidders.bidder)
                for email in emails:
                    receipent_list = [email.email]
                    send_mail(subject, message, 'no-reply@yaas.com', receipent_list, fail_silently=False)



        data = list(resolved_auction.values())

        return JsonResponse({"resolved_auctions": [d['title'] for d in data]})


def changeLanguage(request, lang_code):
    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code

    auctions = Auction.objects.filter(status="Active").order_by('-created_date')

    if lang_code == "en":
        messages.info(request, "Language has been changed to English ")
    elif lang_code == "sv":
        messages.info(request, _("Language has been changed to Swedish "))
    else:
        messages.info(request, _("Language not selected"))

    return render(request, "home.html", {'auctions': auctions})


def changeCurrency(request, currency_code):
    response = requests.get(url)
    data = response.json()

    # Your JSON object
    usd_rate = data["rates"][currency_code]
    auctions = Auction.objects.filter(status="Active").order_by('-created_date')

    for item in auctions:
        new_pris = round(float(item.minimum_price) * usd_rate, 2)
        item.minimum_price = new_pris

    messages.info(request, "Currency has been changed to " + currency_code)

    return render(request, "home.html", {'auctions': auctions})
