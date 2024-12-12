from django.urls import path
from . import views

urlpatterns = [
    path('profile', views.get_customer_profile, name='get_customer_profile'),
    path('login', views.login_customer,name='login'),
    path('signup',views.signup_customer,name='signup'),
    path('logout',views.logout,name='LogOut'),
    path('address/add',views.add_address,name='Add Address'),
    path('address/delete',views.delete_address,name='Delete Address'),
    path('address/update',views.update_address,name='Update Address')
]
