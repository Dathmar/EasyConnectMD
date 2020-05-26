from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('our-story/', views.our_story, name='our-story'),
    path('faqs/', views.faq, name='FAQ'),
    path('faq/', views.faq, name='FAQ'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('connect-with-a-doctor/', views.connect, name='connect-with-a-doctor'),
    path('connect/', views.connect, name='connect-with-a-doctor'),
    path('video-chat/<str:sid>/', views.video_chat, name='video-chat'),
]