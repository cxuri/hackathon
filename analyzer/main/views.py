from django.shortcuts import render

# Create your views here.

from . import views


def Home(request):
    return render(request, "homepage.html")
