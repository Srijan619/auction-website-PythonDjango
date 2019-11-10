from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail, EmailMultiAlternatives
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render
from .models import Auction, Bidding
from user.models import UserLanguage
from django.urls import reverse
from django.utils import translation
from django.contrib.auth.models import User
from django.http import  HttpResponseRedirect, JsonResponse
from .forms import CreateAuctionForm, EditAuctionForm, BiddingForm, GenerateData
from django.utils.translation import gettext as _
from _datetime import datetime, timezone
from faker import Faker
import requests
import random



url = 'https://api.exchangerate-api.com/v4/latest/EUR'


def index(request):
    request.session['ln'] = "en"
    request.session['currency_code'] = "EUR"
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
                subject = ("Auction created")
                message = (
                        "Thank you for creating an auction. Copy and paste the link provided below to edit the auction.")
                link = "http://127.0.0.1:8000/auction/editlink/" + str(new_auction.uuid)+'/'
                to_email = [request.user.email]
                send_mail(subject, message+' '+link, 'no-reply@yaas.com', to_email, fail_silently=False)

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
        if auction is not None:
            if auction.hosted_by == request.user.username:
                print(request.user.username)
                print(auction.id)
                form = EditAuctionForm()
                auction.version = 1
                return render(request, "edit_auction.html", {"form": form})
            else:
                messages.info(request, "That is not your auction to edit")
                return HttpResponseRedirect(reverse("auction:index"))
        else:
            messages.info(request, "No such auction")
            return HttpResponseRedirect(reverse("auction:index"))

    def post(self, request, id):
        auction = Auction.objects.get(id=id)
        if auction is not None:
            if auction.hosted_by == request.user.username:
                form = EditAuctionForm(request.POST)
                if form.is_valid():
                    cd = form.cleaned_data
                    auction.version = auction.version + 1
                    title = cd['title']
                    description = cd['description']
                    auction.description = description
                    auction.title = title
                    auction.save()
                    print(auction.version)
                    messages.info(request, _("Auction has been updated successfully"))
                    return HttpResponseRedirect(reverse("auction:index"))
                else:
                    return render(request, "edit_auction.html", {"form": form})
            else:
                messages.info(request, _("That is not your auction"))
                return HttpResponseRedirect(reverse("auction:index"))
        else:
            messages.info(request, "No such auction")
            return HttpResponseRedirect(reverse("auction:index"))


@method_decorator(login_required, name="dispatch")
class bid(View):
    def get(self, request, item_id):
        response = requests.get(url)
        data = response.json()

        # Your JSON object
        if request.session.get('currency_code') is None:
            request.session['currency_code']= "EUR"

        usd_rate = data["rates"][request.session.get('currency_code')]

        auction = Auction.objects.get(id=item_id)
        auctions = Auction.objects.filter(status="Active")
        bidding_all = Bidding.objects.filter(auction_id=item_id).order_by('-new_price')
        biddings = Bidding.objects.filter(auction_id=item_id).order_by('new_price').last()

        # Converting auction price to usd and vice versa
        new_pris = round(float(auction.minimum_price) * usd_rate, 2)
        auction.minimum_price = new_pris


        # Converting all biddings price
        if bidding_all is not None:
            for item in bidding_all:
              item.new_price=round(float(item.new_price) * usd_rate, 2)

        # Converting the current highest bid
        if biddings is not None:
            biddings.new_price=round(float(biddings.new_price) * usd_rate, 2)


        delta = auction.deadline_date - datetime.now(timezone.utc)

        current_version=auction.version
        request.session['value'] = current_version

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
        if request.session.get('value') is None:
            request.session['value']=0
        if (request.session.get('value') == auction.version): #Checking concurrent sessions
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

        else:
            messages.info(request, "You dont have latest information from the auction")
            return render(request, "bid_auction.html",
                          {"form": form, "auction": auction, "bidding_all": bidding_all, "biddings": biddings})


@login_required()
def ban(request, item_id):
    if request.user.is_superuser:
        auction = Auction.objects.get(id=item_id)

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
    # displaying lists of banned auctions
    def get(self, request):
        auctions = Auction.objects.filter(status="Banned").order_by('-created_date')
        return render(request, "banned_auctions.html", {"auctions": auctions})


def resolve(request):
    if request.method == "GET":
        auctions = Auction.objects.filter(status="Active")
        resolved_auction = Auction.objects.filter(status="Resolved")

        if auctions is not None:
            for auction in auctions:
                delta = auction.deadline_date - datetime.now(timezone.utc)
                if (delta.total_seconds() <= 0):
                    auction.status = "Resolved"
                    auction.save()


            for resolve_auction in resolved_auction:
                bidding = Bidding.objects.filter(auction_id=resolve_auction.id).order_by('new_price').last()
                if bidding is not None:
                    user = User.objects.get(username=resolve_auction.hosted_by)

                    ## Email to the Winner

                    bidder_winner=User.objects.get(username=bidding.bidder)
                    subject_w = _("Winner")
                    message3 = _("Hello bidder, You won the auction. ")
                    to_email3 = [bidder_winner.email]
                    send_mail(subject_w, message3, 'no-reply@yaas.com', to_email3, fail_silently=False)


                    ## Email to the Hosts
                    subject = _("Resolved")
                    message2 = _("Hello Hosts, Your auctions were resolved ")
                    to_email2 = [user.email]
                    send_mail(subject, message2, 'no-reply@yaas.com', to_email2, fail_silently=False)

                    ## Email to the remaining Bidders

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
        request.session['ln'] = lang_code
        messages.info(request, "Language has been changed to English ")
    elif lang_code == "sv":
        request.session['ln'] = lang_code
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
    request.session['currency_code'] = currency_code

    for item in auctions:
        new_pris = round(float(item.minimum_price) * usd_rate, 2)
        item.minimum_price = new_pris

    messages.info(request, "Currency has been changed to " + currency_code)

    return render(request, "home.html", {'auctions': auctions})

@method_decorator(login_required, name="dispatch")
class generateData(View):
    def get(self, request):
        form = GenerateData()
        return render(request, "generate_data.html", {"form": form})

    def post(self, request):
        form = GenerateData(request.POST)
        fake = Faker()
        fake.unique_mode = True
        if form.is_valid():
            cd = form.cleaned_data
            auction_amount = cd['auction_amount']
            list_username =[]
            new_price=[]
            hosted=[]
            auction_id=[]

            for _ in range(0, auction_amount):

                ## Creating random user details

                username = fake.first_name()
                list_username.append(username)


                email = fake.email()
                password = fake.last_name()
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()

                ## creating language session default data

                language = UserLanguage.objects.create(language="en", user_id=user.id)
                language.save()

                ## Creating random auctions

                title = fake.sentence(nb_words=4)
                description = fake.sentence(nb_words=10)
                deadline_date = fake.date_time_between(start_date="+4d", end_date="+30d", tzinfo=None)
                minimum_price =random.randrange(1,1000)
                hosted_by = username
                new_auction = Auction.objects.create(title=title, description=description,
                 minimum_price=minimum_price,
                 deadline_date=deadline_date, hosted_by=hosted_by)
                new_auction.save()


                ## Creating random bids for each auctions

                bid_price=random.randrange(minimum_price,1500)
                new_price.append(bid_price)
                hosted.append(username)
                auction_id.append(new_auction.id)


            # Reversing the list so that hosted by and new bidder wouldnt match
            list_username.reverse()
            #Creating a new random bid
            for i in range(0,auction_amount):
                bids = Bidding.objects.create(new_price=new_price[i], hosted_by=hosted[i],
                bidder=list_username[i], auction_id=auction_id[i])
                bids.save()

            messages.info(request, "Random users and auctions created")
            return HttpResponseRedirect(reverse("auction:index"))


# sending user special link to edit the auction
class EditAuctionLink(View):

    def get(self, request, uuid):
        auction = Auction.objects.get(uuid=uuid) # using the hash uuid stored in database to get the auction
        form = EditAuctionForm()
        auction.version = 1
        return render(request, "edit_auction.html", {"form": form})


    def post(self, request, uuid):
        auction = Auction.objects.get(uuid=uuid)

        form = EditAuctionForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            auction.version = auction.version + 1
            title = cd['title']
            description = cd['description']
            auction.description = description
            auction.title = title
            auction.save()
            print(auction.version)
            messages.info(request, "Auction has been updated successfully")
            return HttpResponseRedirect(reverse("auction:index"))
        else:
            return render(request, "edit_auction.html", {"form": form})
