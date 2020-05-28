from django.shortcuts import get_object_or_404, render
import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Create your views here.
def index(request):
    return render(request, 'EasyConnect/templates/template_reference/index.html')


def our_story(request):
    return render(request, 'EasyConnect/templates/template_reference/our-story.html')


def faq(request):
    return render(request, 'EasyConnect/templates/template_reference/faq.html')


def privacy_policy(request):
    return render(request, 'EasyConnect/templates/template_reference/privacy-policy.html')


def connect(request):
    return render(request, 'EasyConnect/templates/template_reference/connect.html')


def video_chat(request, sid):
    return HttpResponse(f"Hello, world. You're at the EasyConnect video chat page with sid {sid}")
