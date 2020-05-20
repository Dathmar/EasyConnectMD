from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the EasyConnect index.")





"""
    path('admin/', admin.site.urls),
    path('faqs/', faqs.urls),
    path('our-story/', our_story.urls),
    path('connect-with-a-doctor/', connect_with_a_doctor.urls),
    path('doctor/', doctor.urls)
"""