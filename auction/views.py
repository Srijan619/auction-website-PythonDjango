from django.contrib import messages
from django.conf import  settings
from django.core.mail import  send_mail
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.shortcuts import render, get_object_or_404
from .models import Auction
from django.urls import reverse
from django.utils import translation
from django.http import HttpResponse, HttpResponseRedirect
from .forms import CreateAuctionForm,EditAuctionForm,Auction
from django.utils.translation import gettext as _
from _datetime import datetime, timezone

def index(request):

    auctions = Auction.objects.filter(status="Active").order_by('-created_date')
    return render(request, "home.html", {"auctions": auctions})


def search(request):

     if request.GET["term"] != "": # term is just a reference to search check html for search
         criteria =request.GET["term"].strip()
         auctions = Auction.objects.filter(title__icontains=criteria,status="Active").order_by('-created_date')
     else:
         auctions = Auction.objects.filter(status="Active").order_by('-created_date')

     return render(request,"home.html", {'auctions':auctions})


@method_decorator(login_required, name="dispatch")
class CreateAuction(View):
    def get(self,request):
        form= CreateAuctionForm()
        return render(request, "create_auction.html",{"form":form})

    def post(self, request):
        form=CreateAuctionForm(request.POST)

        if form.is_valid():
            cd= form.cleaned_data

            deadline=cd.get("deadline_date")
            tday=datetime.now(timezone.utc)

            time_diff=deadline-tday
            hour=time_diff.total_seconds()/3600.0
            print(hour)

            hosted_by= request.user.username
            if(hour >= 72):
               new_auction=Auction.objects.create(title=cd["title"], description=cd["description"], minimum_price=cd["minimum_price"],
                                               deadline_date=cd["deadline_date"], hosted_by=hosted_by)

               new_auction.save()
               subject=_("Auction created")
               message=_("Thank you for creating an auction. Below link provides to modify the auction details.")
               to_email= [request.user.email]

               send_mail(subject,message,'no-reply@yaas.com',to_email,fail_silently=False)
               messages.info(request, _("Auction has been created successfully, check your emails"))
               return HttpResponseRedirect(reverse("auction:index"))
            else:
                messages.info(request,_("The deadline date should be at least 72 hours from now"))
                return render(request,"create_auction.html",{"form":form})


        else:
            print("Invalid date")
            return render(request, "create_auction.html", {"form":form})

@method_decorator(login_required, name="dispatch")
class EditAuction(View):

   def get(self,request,id):
        auction = Auction.objects.get(id=id)
        if auction.hosted_by == request.user.username:
            form=EditAuctionForm()
            return render(request, "create_auction.html", {"form": form})
        else:
            messages.info(request,_("This is not your auction"))
            return HttpResponseRedirect(reverse("auction:index"))
   def post(self,request,id):
        auction= Auction.objects.get(id=id)
        if auction.hosted_by== request.user.username:
            form = EditAuctionForm(request.POST)
            if form.is_valid():
                cd=form.cleaned_data
                title=cd['title']
                description=cd['description']
                auction.description=description
                auction.title=title
                auction.save()
                messages.info(request,_("Auction has been updated successfully"))
                return HttpResponseRedirect(reverse("auction:index"))
            else:
                return render(request, "create_auction.html", {"form": form})
        else:
            messages.info(request, _("This is not your auction"))
            return HttpResponseRedirect(reverse("auction:index"))

def bid(request, item_id):
    pass


def ban(request, item_id):
    pass


def resolve(request):
    pass


def changeLanguage(request, lang_code):

    translation.activate(lang_code)
    request.session[translation.LANGUAGE_SESSION_KEY] = lang_code

    auctions = Auction.objects.filter(status="Active").order_by('-created_date')

    if lang_code=="en":
     messages.info(request,"Language has been changed to English ")
    elif lang_code=="sv":
     messages.info(request, _("Language has been changed to Swedish "))
    else:
     messages.info(request,_("Language not selected"))

    return render(request,"home.html", {'auctions':auctions})


def changeCurrency(request, currency_code):

    auctions=Auction.objects.filter(status="Active").order_by('-created_date')

    return render(request, "home.html", {'auctions':auctions})


