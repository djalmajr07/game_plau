from django.urls import path
from . import views

urlpatterns = [
    path('', views.GameListView.as_view(), name='games-list'),
    path('game/<int:pk>/', views.GameDetailView.as_view(), name='game-detail'),
    path('log/add/', views.GameLogCreateView.as_view(), name='log-create'),
]
