from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponseBadRequest, HttpResponse
from django.shortcuts import render, redirect
from django.template import loader
from django.urls import reverse
from django.utils import translation
from django.utils.decorators import method_decorator
from django.views import View
from django.template.loader import render_to_string, get_template
from django.contrib.auth.models import User, auth
from django.contrib.auth import update_session_auth_hash
from .models import UserLanguage



class SignUp(View):
    def get(self, request):
        return render(request, 'sign_up.html')

    def post(self, request):

        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        email = request.POST.get('email', '')

        if username == "" or password == "" or email == "":
            messages.info(request, "Check all the fields")
            return render(request, "sign_up.html")
        else:
            if User.objects.filter(username=username).exists():
                messages.info(request, "This username has been taken")
                return render(request, "sign_up.html")

            elif User.objects.filter(email=email).exists():
                messages.info(request, "This email has been taken")
                return render(request, "sign_up.html")
            else:
                if request.session.get('ln') is None:
                    request.session['ln']="en"
                user = User.objects.create_user(username=username, password=password, email=email)
                language=UserLanguage.objects.create(language=request.session.get('ln'), user=user)
                language.save()
                user.save()
                return HttpResponseRedirect(reverse('signin'))


class SignIn(View):
    def get(self, request):

        return render(request, "log_in.html")

    def post(self, request):
        username = request.POST.get('username', '')  # later part username is coming from html file
        password = request.POST.get('password', '')

        user = auth.authenticate(username=username, password=password)

        if username != "" and password != "":
            if user is not None and user.is_active:
                auth.login(request, user)
                language = UserLanguage.objects.get(user_id=request.user.id)
                translation.activate(language.language)
                request.session[translation.LANGUAGE_SESSION_KEY] = language.language
                print("User found")
                return redirect('/')
            else:
                messages.info(request, "Invalid credentials")
                print("No user")
            return redirect('signin')
        else:
            messages.info(request, "Please provide username and password")
            return redirect('signin')

@login_required()
def signout(request):
    auth.logout(request)
    return redirect('/')

@method_decorator(login_required, name="dispatch")
class EditProfile(View):

    def get(self, request):
      return render(request, "profile.html")

    def post(self, request):

        email = request.POST.get('email', '')  # later part username is coming from html file
        password = request.POST.get('password', '')
        user = request.user

        if User.objects.filter(email=email).exists():
             messages.info(request, "Email exits")
             return render(request, "profile.html")

        else:
             user.email = email
             user.set_password(password)
             user.save()
             update_session_auth_hash(request, user)
             messages.info(request, "Updated successfully")
             return HttpResponseRedirect(reverse('signin'))


