"""ayurtantra_webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('api/v1/',include('api.urls')),
    path('api/accounts/', include('dj_rest_auth.urls')),#user management for api browsing without user sign up
    path('api/accounts/registration/', include('dj_rest_auth.registration.urls')),#user sign up via api browsing works along with all-auth
    #path('api-auth/', include('rest_framework.urls')),#adds login/logout to browsable api. does not add signup.
    path('admin/', admin.site.urls), #Django admin screen
    path('accounts/',include('allauth.urls')), #all-auth user management for template browsing
    path('', include('homepage.urls')), #homepage
]
