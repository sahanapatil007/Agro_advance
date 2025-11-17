
from django.urls import path
from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('about/',views.about,name='about'),
    path('crop/',views.crop,name="crop"),
    path('recommend/', views.recommend_crop, name='recommend_crop'),
    path('detect/', views.detect_disease, name='detect_disease'),
    path('detect_history/',views.detect_history,name='detect_history'),
    path("contact/",views.contact_view,name='contact'),
    path("custom_admin/", views.custom_admin, name="custom_admin"),
]