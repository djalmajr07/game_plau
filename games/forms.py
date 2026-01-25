from django import forms
# from .models import GameLog


# class GameLogForm(forms.ModelForm):
#     class Meta:
#         model = GameLog
#         fields = '__all__'
#         widgets = {
#             'game': forms.Select(attrs={'class': 'form-control'}),
#             'date_played': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'hours_played': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Hours'}),
#             'score': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Score (0-100)'}),
#             'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Notes about your play session...'}),
#             'screenshot': forms.FileInput(attrs={'class': 'form-control'}),
#         }
