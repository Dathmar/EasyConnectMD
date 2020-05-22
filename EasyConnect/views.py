from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the EasyConnect index.")

def our_story(request):
    return HttpResponse("Hello, world. You're at the EasyConnect our story page.")


def faqs(request):
    return HttpResponse("Hello, world. You're at the EasyConnect the FAQs page.")


def connect_with_a_doctor(request):
    return HttpResponse("Hello, world. You're at the EasyConnect our connect with a doctor page.")


def video_chat(request, sid):
    return HttpResponse(f"Hello, world. You're at the EasyConnect video chat page with sid {sid}")
