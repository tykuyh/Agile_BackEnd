"""Agile_BackEnd URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
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
from get_backend import views as get_backend_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('user/login/<str:code>', get_backend_views.wechat_login),
    path('search/<str:keyword>/',get_backend_views.search),
    path('activities/images/<str:uid>/',get_backend_views.addPicture),
    path('activities/add/<str:uid>/',get_backend_views.addActivity),
    path('activities/detail/<str:uid>/',get_backend_views.getUserOpenActivities),
    path('activities/attended/<str:uid>/',get_backend_views.getUserAttendActivities),
    path('attend/<str:aid>/<str:uid>/<str:mid>/', get_backend_views.sign),
    path('activities/<str:uid>/<str:aid>/attend/',get_backend_views.attendActivity),
    path('activities/<str:uid>/<str:aid>/cancel/',get_backend_views.cancelActivity),
    path('activities/<str:pageNo>/<str:pageSize>/',get_backend_views.getActivities),
    path('activities/<str:aid>/',get_backend_views.getOneActivity),

]
