# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""

# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import LoginForm, SignUpForm
from swMetrics.home.models import UsrLgn


def login_view(request):
    form = LoginForm(request.POST or None)
    msg = None
    if request.method == "POST":

        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = 'Invalid credentials'
        else:
            msg = 'Error validating the form'

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


def register_view(request):
    msg = None
    success = False

    if request.method == "POST":
        form = SignUpForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get("username")
            raw_password = form.cleaned_data.get("password1")
            Email = form.cleaned_data.get("email")
            EmpId = form.cleaned_data.get("EmpId")
            print(EmpId)
            
            user = authenticate(username=username, password=raw_password)
            print(user)

            msg = 'User created - please <a href="/login">login</a>.'
            success = True
            USR_Obj=UsrLgn(UsrLgnName=username,UsrLgn_Email=Email,UsrLgn_EmpId=EmpId)
            USR_Obj.save(force_insert=True)

            # return redirect("/login/")

        else:
            msg = 'Form is not valid'
    else:
        form = SignUpForm()

    return render(request, "accounts/register.html", {"form": form, "msg": msg, "success": success})

def index(request):
    msg = None
    success = False
    form=None
    return render(request, "home/index.html", {"form": form, "msg": msg, "success": success})




def logout(request):
    msg = None
    success = False
    form=None
    return render(request, "accounts/logout.html", {"form": form, "msg": msg, "success": success})

