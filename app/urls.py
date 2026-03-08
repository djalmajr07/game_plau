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
from games.views import GameListView, NewGameCreateView, GameDetailView, GameUpdateView, GameDeleteView, landing_page, search_games, search_game_covers, update_game_cover, beaten_games
from accounts.views import login_view, register_view, logout_view

urlpatterns = [
    path('', landing_page, name='landingpage'),
    path('admin/', admin.site.urls),
    path('games/', GameListView.as_view(), name='game_list'),
    path('game/<int:pk>/', GameDetailView.as_view(), name='game_detail'),
    path('game/<int:pk>/edit/', GameUpdateView.as_view(), name='edit_game'),
    path('game/<int:pk>/delete/', GameDeleteView.as_view(), name='delete_game'),
    path('game_log/', NewGameCreateView.as_view(), name='new_gameplay'),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
    path('api/search/',search_games, name='search_games'),
    path('api/search-covers/', search_game_covers, name='search_game_covers'),
    path('api/update-cover/', update_game_cover, name='update_game_cover'),
    path('api/beaten-games/', beaten_games, name='beaten_games'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

