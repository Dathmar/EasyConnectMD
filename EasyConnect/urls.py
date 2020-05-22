from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('our-story/', views.our_story, name='our-story'),
    path('faqs/', views.faqs, name='FAQs'),
    path('connect-with-a-doctor/', views.connect_with_a_doctor, name='connect-with-a-doctor'),
    path('video-chat/<str:sid>/', views.video_chat, name='video-chat'),
]