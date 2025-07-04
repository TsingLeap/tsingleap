"""tsingleap_backend URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from users.views import register, login, send_verification_code, get_csrf_token

urlpatterns = [
    path("admin/", admin.site.urls),
    path("register/", register, name="register"),
    path("login/", login, name="login"),
    path("send_verification_code/", send_verification_code, name="send_verification_code"),
    path("get_csrf_token/", get_csrf_token, name="get_csrf_token"),
    path("settings/", include("settings.urls")),
    path("competitions/", include("competitions.urls")),
    path("forum/", include("forum.urls")),
    path("tag/", include("tag.urls")),
]
