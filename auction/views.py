from django.views import View
from django.shortcuts import render
from .models import Auction
from django.http import HttpResponse



def index(request):
    auctions = Auction.objects.filter(status_exact="Active").order_by('created_date')
    return render(request, "base.html", {"auctions":auctions})



def search(request):
    term = request.GET("term")
    auctions = Auction.objects.filter(status_exact="Active", title__contains=term).order_by('created_date')
    return render(request, "archive.html", {"auctions":auctions})


class CreateAuction(View):
    def get(self, request):
        form = CreateBlogForm()
        return render(request, "createblog.html", {"form": form})

    def post(self, request):
        form = CreateBlogForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            b_title = cd["title"]
            b_body = cd["body"]

            b = blog(title=b_title, body=b_body)
            b.save()
            return HttpResponseRedirect(reverse("homepage"))
        else:
            return render(request, "createblog.html", {"form": form})


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


