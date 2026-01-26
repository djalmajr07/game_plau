from django.contrib import admin
from .models import Console, GameStatus, Game

# Register your models here.
class ConsoleAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)

class GameStatusAdmin(admin.ModelAdmin):
    list_display = ('id', 'status')
    search_fields = ('status',)

class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'console', 'release_year', 'rating', 'status')
    search_fields = ('title', 'console__name', 'status__status')
    list_filter = ('console', 'status')

admin.site.register(Console, ConsoleAdmin)
admin.site.register(GameStatus, GameStatusAdmin)
admin.site.register(Game, GameAdmin)