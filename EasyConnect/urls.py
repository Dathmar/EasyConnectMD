from django.urls import path, include
from django.conf.urls import url
from EasyConnect.views import provider_dashboard
from . import views

app_name = 'easyconnect'
urlpatterns = [
    # default views
    path('', views.index, name='index'),
    path('our-story/', views.our_story, name='our-story'),
    path('faqs/', views.faq, name='faq'),
    path('faq/', views.faq, name='faq'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('splash-page/', views.splash_page, name='splash-page'),
    path('connect/', views.connect, name='connect-with-a-doctor'),
    path('connect-with-a-doctor/', views.connect, name='connect-with-a-doctor'),
    path('connect-2/<uuid:patient_id>', views.connect_2, name='connect-2'),
    path('video-chat/<uuid:patient_id>', views.video_chat, name='video-chat'),


    #loading data
    path('icd10-load/', views.icd10_load, name='icd10-load'),
    path('affiliate-load/', views.affiliate_load, name='affiliate-load'),

    #server health
    path('server-time/', views.server_time, name='server-time'),
    path('connect-timeless/', views.connect_timeless, name='connect-timeless'),

    # in dev
    path('lucky-provider/', views.lucky_provider, name='lucky_provider'),

    # provier side
    path('provider/<uuid:patient_id>', views.provider_view, name='provider-view'),
    url(r'^dashboard/', provider_dashboard, name='dashboard'),
    url(r'^accounts/', include("django.contrib.auth.urls")),
    path('accounts/logout/', views.logout_request, name='logout'),
    path('accounts/login/', views.login_request, name='login'),
    path('video-token/', views.video_token, name='video-token'),
    path('apply-coupon/', views.apply_coupon, name='apply-coupon'),
    path('patient-cost/', views.patient_cost, name='patient-cost'),
    path('square-app-id/', views.square_app_id, name='square-app-id'),

    #affiliate views
    path('<slug:affiliate_url>/', views.index_affiliate, name='index-affiliate'),
    path('<slug:affiliate_url>/our-story/', views.our_story_affiliate, name='our-story-affiliate'),
    path('<slug:affiliate_url>/faqs/', views.faq_affiliate, name='faq-affiliate'),
    path('<slug:affiliate_url>/privacy-policy/', views.privacy_policy_affiliate, name='privacy-policy-affiliate'),
    path('<slug:affiliate_url>/connect/', views.connect_affiliate, name='connect-with-a-doctor-affiliate'),
    path('<slug:affiliate_url>/connect-with-a-doctor/', views.connect_affiliate, name='connect-with-a-doctor-affiliate'),
    path('<slug:affiliate_url>/connect-2/<uuid:patient_id>', views.connect_2_affiliate, name='connect-2-affiliate'),
    path('<slug:affiliate_url>/video-chat/<uuid:patient_id>', views.video_chat_affiliate, name='video-chat-affiliate'),
]
