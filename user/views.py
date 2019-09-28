from django.contrib import messages
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views import View
from django.contrib.auth.models import User, auth
from .models import Account


class SignUp(View):
   def get(self, request):
       return render(request, 'sign_up.html')

   def post(self, request):

       username = request.POST['username']
       password = request.POST['password']
       email = request.POST['email']


       if  username==""  and password=="" and email=="":
           messages.info(request, "Check all the fields")
           return render(request,"signup",context)
       else:
           if User.objects.filter(username=username).exists():
               messages.info(request, "This username has been taken")
               return render(request,"signup")
           elif User.objects.filter(email=email).exists():
               messages.info(request, "Email exits")
               return render(request,"signup")
           else:
               user = User.objects.create_user(username=username, password=password, email=email)
               user.save()
               messages.info(request, "Please log in")
               return HttpResponseRedirect(reverse("signin"))



class SignIn(View):
    def get(self, request):
        print("Get_request")
        return render(request, "log_in.html")

    def post(self, request):
        username = request.POST.get('username', '') #later part username is coming from html file
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)
        if username!="" and password!="":
           if user is not None and user.is_active:
            auth.login(request, user)
            print("User found")
            return redirect('/')
           else:
            messages.info(request, "Invalid credentials")
            print("No user")
           return redirect('signin')
        else:
         messages.info(request, "Please provide username and password")
         return redirect('signin')



def signout(request):
    auth.logout(request)
    return redirect('/')


class EditProfile(View):
    pass
