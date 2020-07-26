from django.urls import path, include

from . import views

app_name = 'easyconnect'
urlpatterns = [
    path('', views.index, name='index'),
    path('our-story/', views.our_story, name='our-story'),
    path('faqs/', views.faq, name='faq'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('connect/', views.connect, name='connect-with-a-doctor'),
    path('connect-with-a-doctor/', views.connect, name='connect-with-a-doctor'),
    path('connect-2/<uuid:patient_id>', views.connect_2, name='connect-2'),
    path('video-chat/<uuid:patient_id>', views.video_chat, name='video-chat'),
    #path('provider/', views.provider_list_view, name='provider-list-view'),
    path('provider/<uuid:patient_id>', views.provider_view, name='provider-view'),

]