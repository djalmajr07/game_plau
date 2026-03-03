from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView
from django.urls import reverse_lazy
from .models import Game
from django.contrib.auth.mixins import LoginRequiredMixin

class GameListView(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'home.html'
    context_object_name = 'games'

    def get_queryset(self):
        games = Game.objects.filter(owner=self.request.user).order_by('title')
        search = self.request.GET.get('search')
        if search:
            games = games.filter(title__icontains=search)
        return games

class NewGameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    fields = ['title', 'console', 'release_year', 'photo', 'rating', 'status']
    template_name = 'new_game_log.html'
    success_url = reverse_lazy('game_list')


class GameDetailView(LoginRequiredMixin, DetailView):
    model = Game
    template_name = 'game_detail.html'

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)
    
def landing_page(request):
    featured_games = Game.objects.filter(landingpage_game=True)
    return render(request, 'landing_page.html', {'games': featured_games})

# class GameLogCreateView(CreateView):
#     model = GameLog
#     form_class = GameLogForm
#     template_name = 'game_log_form.html'
#     success_url = reverse_lazy('games_list')

