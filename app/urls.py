"""
URL configuration for app project.

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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from games.views import GameListView, NewGameCreateView, GameDetailView, landing_page
from accounts.views import login_view, register_view, logout_view

urlpatterns = [
    path('', landing_page, name='landingpage'),
    path('admin/', admin.site.urls),
    path('games/', GameListView.as_view(), name='game_list'),
    path('game/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('game_log/', NewGameCreateView.as_view(), name='new_gameplay'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

