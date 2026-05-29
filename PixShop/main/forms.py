from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name',
                  'middle_name', 'adress')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            field.widget.attrs.update(
                {'class': 'form-controol', 
                 'style': 'font-family: monospace;'}
            )