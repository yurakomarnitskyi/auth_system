from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import TemplateView
from accounts.views import request_public_key


urlpatterns = [
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')), 
    path('questions/', include('product_questions.urls')),
    path('favorites/', include('favorites.urls')),
    path('jwk/', request_public_key)
]


# urlpatterns += [re_path(r'^.*', TemplateView.as_view(template_name='index.html'))]
