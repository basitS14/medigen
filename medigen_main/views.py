from django.shortcuts import render
from django.http import HttpResponse

def home(request):
    return render(request , 'index.html')

def know_more(request):
    return render(request , 'know.more.html')

def sign_up(request):
    return render(request , "")
