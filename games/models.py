from django.db import models
from django.conf import settings

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
    console = models.ForeignKey(Console, on_delete=models.PROTECT, related_name='game_console')
    photo = models.ImageField(upload_to='media/', blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    status = models.ForeignKey(GameStatus, on_delete=models.PROTECT, related_name='game_status')
    release_year = models.IntegerField(blank=True, null=True)
    # price = models.FloatField(blank=True, null=True)
    # description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title
        

# class GameLog(models.Model):
#     id = models.AutoField(primary_key=True)
#     game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='logs')
#     date_played = models.DateField()
#     hours_played = models.FloatField(blank=True, null=True)
#     score = models.IntegerField(blank=True, null=True)
#     notes = models.TextField(blank=True, null=True)
#     screenshot = models.ImageField(upload_to='screenshots/', blank=True, null=True)
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-date_played']

#     def __str__(self):
#         return f'{self.game.title} - {self.date_played}'

# class GameInventory(models.Model):
#     games_count = models.IntegerField()
#     games_value = models.FloatField()
#     created_at = models.DateTimeField(auto_now_add=True)

#     class Meta:
#         ordering = ['-created_at'] 

#     def __str__(self):
#         return f'{self.games_count} - {self.games_value}'