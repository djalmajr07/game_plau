from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, DetailView, UpdateView, DeleteView
from django.urls import reverse_lazy
from .models import Game
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from datetime import datetime

class GameListView(LoginRequiredMixin, ListView):
    model = Game
    template_name = 'home.html'
    context_object_name = 'games'
    paginate_by = 50

    def get_queryset(self):
        games = Game.objects.filter(owner=self.request.user).order_by('title')
        tab = self.request.GET.get('tab', 'played')
        search = self.request.GET.get('search', '').strip()
        
        # Filter by tab (case-insensitive, strip whitespace)
        if tab == 'playing':
            games = games.filter(status__status__iexact='jogando')
        elif tab == 'played':
            games = games.filter(status__status__iexact='platinado') | games.filter(status__status__iexact='historia completa')
        elif tab == 'by_year':
            year = self.request.GET.get('year', '').strip()
            if year:  # Only filter if year is provided and not empty
                games = games.filter(completion_date__year=year)
            # else: show all games when no year is selected
        elif tab == 'by_console':
            console_id = self.request.GET.get('console', '').strip()
            if console_id:  # Only filter if console_id is provided and not empty
                games = games.filter(console_id=console_id)
            # else: show all games when no console is selected
        elif tab == 'next':
            games = games.filter(status__status__iexact='na lista de proximo')
        
        # Apply search filter on top of tab filter
        if search:
            games = games.filter(title__icontains=search)
        
        return games
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_games = Game.objects.filter(owner=self.request.user)
        
        # Build tab counts and data
        context['active_tab'] = self.request.GET.get('tab', 'played')
        context['search_query'] = self.request.GET.get('search', '').strip()
        
        # Tab counts (case-insensitive)
        context['count_playing'] = user_games.filter(status__status__iexact='jogando').count()
        context['count_played'] = (user_games.filter(status__status__iexact='platinado') | user_games.filter(status__status__iexact='historia completa')).count()
        context['count_next'] = user_games.filter(status__status__iexact='na lista de proximo').count()
        
        # Check if year filter is active
        selected_year = self.request.GET.get('year', '').strip()
        context['selected_year'] = selected_year
        
        # Statistics for dashboard (case-insensitive) - adapt to year filter
        if context['active_tab'] == 'by_year' and selected_year:
            # Filter by selected year using completion_date
            context['total_games'] = (user_games.filter(status__status__iexact='platinado', completion_date__year=selected_year) | user_games.filter(status__status__iexact='historia completa', completion_date__year=selected_year)).count()
            context['current_year'] = int(selected_year)
            context['games_played_this_year'] = context['total_games']  # Same as total_games for the filtered year
            context['games_not_started'] = user_games.filter(completion_date__year=selected_year).exclude(
                status__status__iexact='platinado'
            ).exclude(
                status__status__iexact='historia completa'
            ).exclude(
                status__status__iexact='jogando'
            ).exclude(
                status__status__iexact='na lista de proximo'
            ).count()
        else:
            # Default: show current year statistics
            context['current_year'] = datetime.now().year
            context['total_games'] = (user_games.filter(status__status__iexact='platinado') | user_games.filter(status__status__iexact='historia completa')).count()
            context['games_played_this_year'] = (
                user_games.filter(status__status__iexact='platinado', completion_date__year=datetime.now().year) | 
                user_games.filter(status__status__iexact='historia completa', completion_date__year=datetime.now().year)
            ).count()
            context['games_not_started'] = user_games.exclude(
                status__status__iexact='platinado'
            ).exclude(
                status__status__iexact='historia completa'
            ).exclude(
                status__status__iexact='jogando'
            ).exclude(
                status__status__iexact='na lista de proximo'
            ).count()
        
        # Get unique years and consoles for filters (using completion_date)
        from django.db.models.functions import ExtractYear
        context['years'] = sorted(
            set(user_games.filter(completion_date__isnull=False).annotate(year=ExtractYear('completion_date')).values_list('year', flat=True)),
            reverse=True
        )
        context['consoles'] = user_games.values_list('console', flat=True).distinct()
        from .models import Console
        context['console_objects'] = Console.objects.filter(id__in=context['consoles'])
        
        # Selected filters
        context['selected_console'] = self.request.GET.get('console')
        
        return context

class NewGameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    fields = ['title', 'console', 'status']
    template_name = 'new_game_log.html'
    success_url = reverse_lazy('game_list')

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)

class GameDetailView(LoginRequiredMixin, DetailView):
    model = Game
    template_name = 'game_detail.html'

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

class GameUpdateView(LoginRequiredMixin, UpdateView):
    model = Game
    fields = ['title', 'console', 'status', 'release_year', 'completion_date', 'rating', 'photo_url', 'landingpage_game']
    template_name = 'game_form.html'
    success_url = reverse_lazy('game_list')

    def get_queryset(self):
        return self.model.objects.filter(owner=self.request.user)

class GameDeleteView(LoginRequiredMixin, DeleteView):
    model = Game
    template_name = 'game_confirm_delete.html'
    success_url = reverse_lazy('game_list')

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

import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import Game
import requests
from django.conf import settings

# ===== SEARCH GAMES ENDPOINT =====
@require_http_methods(["GET"])
def search_games(request):
    """
    Endpoint: /games/api/search/?q=god+of+war
    Returns: JSON list of games from IGDB with title, year, and cover URL
    """
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'results': []})
    
    try:
        # Get IGDB Access Token
        client_id = getattr(settings, 'IGDB_CLIENT_ID', None)
        client_secret = getattr(settings, 'IGDB_CLIENT_SECRET', None)
        
        if not client_id or not client_secret:
            return JsonResponse({'error': 'IGDB credentials not configured'}, status=500)
        
        # 1. Authenticate with Twitch/IGDB
        auth_url = 'https://id.twitch.tv/oauth2/token'
        auth_params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        auth_res = requests.post(auth_url, params=auth_params)
        token = auth_res.json().get('access_token')
        
        if not token:
            return JsonResponse({'error': 'Failed to get IGDB token'}, status=500)
        
        # 2. Search IGDB for games
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {token}',
        }
        
        # Search query - returns up to 10 results
        igdb_query = f'''
        search "{query}";
        fields id, name, release_dates.y, cover.image_id;
        limit 10;
        '''
        
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers,
            data=igdb_query
        )
        response.raise_for_status()
        games = response.json()
        
        # 3. Format results for frontend
        results = []
        for game in games:
            cover_url = None
            if game.get('cover') and game['cover'].get('image_id'):
                image_id = game['cover']['image_id']
                cover_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
            
            results.append({
                'igdb_id': game.get('id'),
                'name': game.get('name', 'Unknown'),
                'year': game.get('release_dates', [{}])[0].get('y') if game.get('release_dates') else None,
                'cover_url': cover_url
            })
        
        return JsonResponse({'results': results})
        
    except Exception as e:
        print(f"Search error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# ===== UPDATE COVER ENDPOINT =====
from django.views.decorators.csrf import csrf_exempt

@require_http_methods(["POST"])
def update_game_cover(request):
    """
    Endpoint: /api/update-cover/
    POST data: { game_id: 1, new_cover_url: "https://..." }
    """
    try:
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=401)
        
        data = json.loads(request.body)
        game_id = data.get('game_id')
        new_cover_url = data.get('new_cover_url')
        
        if not game_id or not new_cover_url:
            return JsonResponse({'error': 'Missing game_id or new_cover_url'}, status=400)
        
        # Get the game (only if user owns it)
        game = Game.objects.get(id=game_id, owner=request.user)
        game.photo_url = new_cover_url
        game.save()
        
        print(f"✅ Cover updated for game {game_id}: {new_cover_url}")
        return JsonResponse({'success': True, 'new_url': new_cover_url})
        
    except Game.DoesNotExist:
        return JsonResponse({'error': 'Game not found or not owned by user'}, status=404)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        print(f"❌ Error updating cover: {e}")
        return JsonResponse({'error': str(e)}, status=500)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


# ===== SEARCH ALTERNATIVE COVERS =====
@require_http_methods(["GET"])
def search_game_covers(request):
    """
    Endpoint: /api/search-covers/?title=god+of+war
    Returns: List of games with their covers for selection
    """
    title = request.GET.get('title', '').strip()
    
    if len(title) < 2:
        return JsonResponse({'results': []})
    
    try:
        # Get IGDB Access Token
        client_id = getattr(settings, 'IGDB_CLIENT_ID', None)
        client_secret = getattr(settings, 'IGDB_CLIENT_SECRET', None)
        
        if not client_id or not client_secret:
            return JsonResponse({'error': 'IGDB credentials not configured'}, status=500)
        
        # 1. Authenticate with Twitch/IGDB
        auth_url = 'https://id.twitch.tv/oauth2/token'
        auth_params = {
            'client_id': client_id,
            'client_secret': client_secret,
            'grant_type': 'client_credentials'
        }
        auth_res = requests.post(auth_url, params=auth_params)
        token = auth_res.json().get('access_token')
        
        if not token:
            return JsonResponse({'error': 'Failed to get IGDB token'}, status=500)
        
        # 2. Search IGDB for games - return up to 10 results
        headers = {
            'Client-ID': client_id,
            'Authorization': f'Bearer {token}',
        }
        
        igdb_query = f'''
        search "{title}";
        fields id, name, first_release_date, cover.image_id;
        limit 10;
        '''
        
        response = requests.post(
            'https://api.igdb.com/v4/games',
            headers=headers,
            data=igdb_query
        )
        response.raise_for_status()
        games = response.json()
        
        # 3. Format results for frontend
        results = []
        for game in games:
            cover_url = None
            if game.get('cover') and game['cover'].get('image_id'):
                image_id = game['cover']['image_id']
                cover_url = f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
            
            results.append({
                'url': cover_url,
                'name': game.get('name', 'Unknown'),
                'year': game.get('first_release_date', '')
            })
        
        return JsonResponse({'results': results})
    
    except Exception as e:
        print(f"Cover search error: {e}")
        return JsonResponse({'error': str(e)}, status=500)


# ===== BEATEN GAMES ENDPOINT =====
@require_http_methods(["GET"])
def beaten_games(request):
    """
    Endpoint: /api/beaten-games/?year=2024&console=1
    Returns: List of games beaten by the user (filtered by year/console)
    """
    try:
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'error': 'Not authenticated'}, status=401)
        
        # Get filter parameters
        year = request.GET.get('year')
        console_id = request.GET.get('console')
        
        # Base queryset - only completed games
        queryset = Game.objects.filter(
            owner=user,
            status__status__icontains='completed'  # Adjust based on your status names
        ).order_by('-completion_date', '-release_year')
        
        # Filter by year if provided
        if year:
            try:
                year = int(year)
                queryset = queryset.filter(completion_date__year=year)
            except:
                pass
        
        # Filter by console if provided
        if console_id:
            try:
                console_id = int(console_id)
                queryset = queryset.filter(console_id=console_id)
            except:
                pass
        
        # Format response
        games = []
        for game in queryset[:50]:  # Limit to 50 games per request
            games.append({
                'id': game.id,
                'title': game.title,
                'console': game.console.name,
                'year': game.release_year,
                'photo_url': game.photo_url,
                'rating': game.rating,
                'completion_date': game.completion_date.isoformat() if game.completion_date else None,
            })
        
        return JsonResponse({'games': games})
    
    except Exception as e:
        print(f"Error fetching beaten games: {e}")
        return JsonResponse({'error': str(e)}, status=500)

