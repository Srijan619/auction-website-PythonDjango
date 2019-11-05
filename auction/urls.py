from django.urls import path, re_path
from . import views


app_name = 'auction'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.search, name='search'),
    path('create/', views.CreateAuction.as_view(), name='create'),
    re_path(r'^edit/(\d+)/$', views.EditAuction.as_view(), name='edit'),
    re_path(r'^bid/(\d+)/$', views.bid.as_view(), name='bid'),
    re_path(r'^ban/(\d+)$', views.ban, name='ban'),
    path('resolve/', views.resolve, name='resolve'),
    path('banned/', views.bannedAuctions.as_view(), name="banned"),
    path('generate/', views.generateData.as_view(), name="generate"),



]
