from django.urls import path
from . import views

app_name = 'user'
urlpatterns = [
    path('profile/', views.EditProfile.as_view(), name='editprofile'),
    # path('SignIn', views.SignIn, name='sign_in'),
    # path('SignUp', views.SignUp, name='sign_up'),
    path('', views.EditProfile.as_view(), name='user')
]