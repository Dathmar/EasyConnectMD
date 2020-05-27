from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('our-story/', views.our_story, name='our-story'),
    path('faqs/', views.faq, name='faq'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('connect/', views.connect, name='connect-with-a-doctor'),
    path('connect-with-a-doctor/', views.connect, name='connect-with-a-doctor'),
    path('video-chat/<str:sid>/', views.video_chat, name='video-chat'),
]