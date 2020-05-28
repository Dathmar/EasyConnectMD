from django.http import Http404
from django.shortcuts import render
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Create your views here.
def index(request):
    return render(request, 'EasyConnect/index.html')


def our_story(request):
    return render(request, 'EasyConnect/our-story.html')


def faq(request):
    return render(request, 'EasyConnect/faq.html')


def privacy_policy(request):
    return render(request, 'EasyConnect/privacy-policy.html')


def connect(request):
    return render(request, 'EasyConnect/connect.html')


def video_chat(request, sid):
    return HttpResponse(f"Hello, world. You're at the EasyConnect video chat page with sid {sid}")
