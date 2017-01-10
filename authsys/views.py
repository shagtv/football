from django.contrib import auth
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.template.context_processors import csrf
from django.urls import reverse


def login(request):
    args = {}
    args.update(csrf(request))
    if request.POST:
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        user = auth.authenticate(username=username, password=password)
        if user is not None:
            auth.login(request, user)
            return redirect(reverse('home'))
        else:
            args['login_error'] = "User not found"
            messages.add_message(request, messages.ERROR, 'User not found')
    return render(request, "authsys/login.html", args)


def logout(request):
    auth.logout(request)
    return redirect(reverse('home'))


def register(request):
    args = {}
    args.update(csrf(request))
    args['form'] = UserCreationForm()
    if request.POST:
        newuser_form = UserCreationForm(request.POST)
        if newuser_form.is_valid():
            newuser_form.save()
            newuser = auth.authenticate(username=newuser_form.cleaned_data['username'], password=newuser_form.cleaned_data['password1'])
            auth.login(request, newuser)
            return redirect(reverse('home'))
        else:
            args['form'] = newuser_form
    return render(request, "authsys/register.html", args)