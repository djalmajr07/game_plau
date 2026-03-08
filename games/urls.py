from django.urls import path
from . import views

urlpatterns = [
    # Game management views
    path('', views.GameListView.as_view(), name='game_list'),
    path('new/', views.NewGameCreateView.as_view(), name='new_gameplay'),
    path('game/<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    path('game/<int:pk>/edit/', views.GameUpdateView.as_view(), name='edit_game'),
    path('game/<int:pk>/delete/', views.GameDeleteView.as_view(), name='delete_game'),
    
    # API endpoints for autocomplete and cover selection
    path('api/search/', views.search_games, name='search_games'),
    path('api/search-covers/', views.search_game_covers, name='search_game_covers'),
    path('api/update-cover/', views.update_game_cover, name='update_game_cover'),
    path('api/beaten-games/', views.beaten_games, name='beaten_games'),
]
