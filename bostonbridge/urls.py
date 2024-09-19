"""
URL configuration for bostonbridge project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from bridge import views as bridge_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', bridge_views.home, name='home'),
    path('home', bridge_views.home, name='home'),
    path('login/', bridge_views.login, name='login'),
    path('logout/', bridge_views.logout_view, name='logout'),
    path('register/', bridge_views.register, name='register'),
    path('forgot_password/', bridge_views.forgot_password, name='forgot_password'),
    path('navigation/', bridge_views.navigation, name='navigation'),
    path('add_rc/', bridge_views.add_rc, name='add_rc'),
    path('rental_check/', bridge_views.rental_check, name='rental_check'),
    path('nearby_events/', bridge_views.nearby_events, name='nearby_events'),
    path('rent_predict/', bridge_views.rent_predict, name='rent_predict'),
    path('lyft_uber/', bridge_views.lyft_uber, name='lyft_uber'),
    path('commuter_crowd/', bridge_views.commuter_crowd, name='commuter_crowd'),
    path('student_discount/', bridge_views.student_discount, name='student_discount'),
    
    

]
