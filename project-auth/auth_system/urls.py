from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from  accounts.views import my_view


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')), 
   
    
]

# urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]
