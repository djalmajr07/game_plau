from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
# from .models import Game, GameLog
# from .forms import GameLogForm


# class GameListView(ListView):
#     model = Game
#     template_name = 'games_list.html'
#     context_object_name = 'games'


# class GameDetailView(DetailView):
#     model = Game
#     template_name = 'game_detail.html'
#     context_object_name = 'game'


# class GameLogCreateView(CreateView):
#     model = GameLog
#     form_class = GameLogForm
#     template_name = 'game_log_form.html'
#     success_url = reverse_lazy('games_list')

