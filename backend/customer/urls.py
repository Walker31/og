from django.urls import path
from . import views

urlpatterns = [
    path('profile', views.get_customer_profile, name='get_customer_profile'),
    path('login', views.login_customer,name='login'),
    path('signup',views.signup_customer,name='signup'),
    path('logout',views.logout,name='LogOut')
]
