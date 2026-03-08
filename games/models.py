from django.db import models
from django.conf import settings
import requests 

class Console(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=20)

    def __str__(self):
        return self.name
    
class GameStatus(models.Model):
    id = models.AutoField(primary_key=True)
    status = models.CharField(max_length=20)

    def __str__(self):
        return self.status

class Game(models.Model):
    id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE, 
        related_name='games'
    )
    title = models.CharField(max_length=200)
    console = models.ForeignKey(
        Console, 
        on_delete=models.PROTECT, 
        related_name='games' 
    )
    photo_url = models.URLField(max_length=500, blank=True, null=True)
    rating = models.IntegerField(blank=True, null=True)
    status = models.ForeignKey(
        GameStatus, 
        on_delete=models.PROTECT, 
        related_name='media' 
    )
    release_year = models.IntegerField(blank=True, null=True)
    landingpage_game = models.BooleanField(
        default=False, 
        help_text="Add the game to landing page?"
    )

    def __str__(self):
        return f"{self.title} ({self.console})"

    # --- THE FIX IS HERE ---
    def save(self, *args, **kwargs):
        # Only run if no URL is provided
        if not self.photo_url: 
            print(f"--- Automated Search Starting for: {self.title} ---")
            try:
                image_link = self.fetch_igdb_cover() 
                if image_link:
                    self.photo_url = image_link
                    print(f"--- Found Cover: {image_link} ---")
            except Exception as e:
                print(f"Search failed: {e}")
                
        super().save(*args, **kwargs)

    # Move this out of the save() method (Shift-Tab)
    def fetch_igdb_cover(self):
        client_id = getattr(settings, 'IGDB_CLIENT_ID', None)
        client_secret = getattr(settings, 'IGDB_CLIENT_SECRET', None)
        
        if not client_id or not client_secret:
            print("ERROR: IGDB credentials not configured in settings.py")
            return None

        try:
            # 1. Get Access Token
            auth_url = 'https://id.twitch.tv/oauth2/token'
            auth_params = {
                'client_id': client_id,
                'client_secret': client_secret,
                'grant_type': 'client_credentials'
            }
            auth_res = requests.post(auth_url, params=auth_params)
            auth_res.raise_for_status()
            token = auth_res.json().get('access_token')
            
            if not token:
                return None

            # 2. Search IGDB
            headers = {
                'Client-ID': client_id,
                'Authorization': f'Bearer {token}',
            }
            
            # Use 'search' for broad matching (like Backloggd does)
            query = f'search "{self.title}"; fields cover.image_id; limit 1;'
            response = requests.post('https://api.igdb.com/v4/games', headers=headers, data=query)
            response.raise_for_status()
            data = response.json()
            
            if data and 'cover' in data[0]:
                image_id = data[0]['cover']['image_id']
                # Backloggd uses vertical covers, so we use t_cover_big
                return f"https://images.igdb.com/igdb/image/upload/t_cover_big/{image_id}.jpg"
            else:
                print(f"No results for {self.title}")
                
        except Exception as e:
            print(f"IGDB Request Failed: {e}")
            
        return None