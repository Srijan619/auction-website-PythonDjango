from django.views import View
from django.shortcuts import render
from .models import Auction
from django.http import HttpResponse



def index(request):
    #auctions = Auction.objects.filter(status_exact="Active").order_by('created_date')
    #return render(request, "base.html", {"auctions":auctions})
    return render(request,"home.html")



def search(request):
    #term = request.GET("term")
    #auctions = Auction.objects.filter(status_exact="Active", title__contains=term).order_by('created_date')
   # return render(request, "archive.html", {"auctions":auctions})
   pass


class CreateAuction(View):
    pass

class EditAuction(View):
    pass


def bid(request, item_id):
    pass


def ban(request, item_id):
    pass


def resolve(request):
    pass


def changeLanguage(request, lang_code):
    pass


def changeCurrency(request, currency_code):
    pass


