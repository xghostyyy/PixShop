from django import forms
from django.contrib.auth.forms import (
    UserCreationForm,
    PasswordChangeForm as DjangoPasswordChangeForm,
)
from .models import User

_WIDGET_ATTRS = {'class': 'form-control', 'style': 'font-family: monospace;'}


def _apply_widgets(fields_dict):
    for field in fields_dict.values():
        field.widget.attrs.update(_WIDGET_ATTRS)

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'middle_name', 'adress')
        labels = {
            'email':       'Электронная почта',
            'first_name':  'Имя',
            'last_name':   'Фамилия',
            'middle_name': 'Отчество',
            'adress':      'Адрес доставки',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].label = 'Пароль'
        self.fields['password1'].help_text = (
            'Не менее 8 символов. Не должен совпадать с личными данными. '
            'Не может быть слишком простым или состоять только из цифр.'
        )
        self.fields['password2'].label = 'Подтверждение пароля'
        self.fields['password2'].help_text = 'Введите пароль ещё раз для подтверждения.'
        _apply_widgets(self.fields)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'middle_name', 'adress')
        labels = {
            'first_name':  'Имя',
            'last_name':   'Фамилия',
            'middle_name': 'Отчество',
            'adress':      'Адрес доставки',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        _apply_widgets(self.fields)


class PixPasswordChangeForm(DjangoPasswordChangeForm):
    old_password = forms.CharField(
        label='Текущий пароль',
        strip=False,
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'current-password',
            'autofocus': True,
            'class': 'form-control',
            'style': 'font-family: monospace;',
        }),
    )
    new_password1 = forms.CharField(
        label='Новый пароль',
        strip=False,
        help_text=(
            'Не менее 8 символов. Не должен совпадать с вашими личными данными. '
            'Не может быть слишком простым или состоять только из цифр.'
        ),
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'style': 'font-family: monospace;',
        }),
    )
    new_password2 = forms.CharField(
        label='Подтверждение нового пароля',
        strip=False,
        help_text='Введите новый пароль ещё раз для подтверждения.',
        widget=forms.PasswordInput(attrs={
            'autocomplete': 'new-password',
            'class': 'form-control',
            'style': 'font-family: monospace;',
        }),
    )

    error_messages = {
        'password_incorrect': 'Текущий пароль введён неверно. Попробуйте ещё раз.',
        'password_mismatch': 'Новые пароли не совпадают.',
    }
