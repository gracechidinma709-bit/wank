"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
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
from django.urls import path
from accounts.views import home, signon, dashboard, verify_pin, edit_pin, create_deposit, pay_verification_fee, create_transfer
from django.contrib.auth import views as auth_views


urlpatterns = [
    path('admin/', admin.site.urls),

    path('', home, name='home'),

    path('signon/', signon, name='signon'),

    path('dashboard/', dashboard, name='dashboard'),
    
    path(
        'logout/',
        auth_views.LogoutView.as_view(),
        name='logout'
    ),
    
    path('verify-pin/', verify_pin, name='verify_pin'),
    
    
    path(
    'edit-pin/',
    edit_pin,
    name='edit_pin'
    ),
    
    path('deposit/', create_deposit, name='deposit'),

    path(
        'pay-verification-fee/',
        pay_verification_fee,
        name='pay_verification_fee'
    ),

    path(
        'transfer/create/',
        create_transfer,
        name='create_transfer'
    ),
    
    
]