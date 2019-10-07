from django.urls import path, re_path
from . import views
from auction.rest_api import * # imports all rest api related materials

app_name = 'auction'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('create/', views.CreateAuction.as_view(), name='create'),
    re_path(r'^edit/(\d+)/$', views.EditAuction.as_view(), name='edit'),
    re_path(r'^bid/(\d+)/$', views.bid, name='bid'),
    re_path(r'^ban/(\d+)$', views.ban, name='ban'),
    path('resolve/', views.resolve, name='resolve'),
    path('api/', auction_list, name='auction_api')
]
