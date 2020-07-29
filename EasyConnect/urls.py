from django.urls import path, include
from django.conf.urls import url
from EasyConnect.views import provider_dashboard
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
    path('provider/<uuid:patient_id>', views.provider_view, name='provider-view'),


    url(r'^dashboard/', provider_dashboard, name='dashboard'),
    url(r'^accounts/', include("django.contrib.auth.urls")),
    path('accounts/logout/', views.logout_request, name='logout'),
    path('accounts/login/', views.login_request, name='login'),
    path('accounts/password_change/', views.password_change, name='password-change')
]
