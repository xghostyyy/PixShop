from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    email = models.EmailField(unique=True, 
                              verbose_name='Электронная почта')
    middle_name = models.CharField(max_length=100, blank=True, 
                                   verbose_name='Отчество')
    adress = models.CharField(max_length=100, 
                              verbose_name='Адрес доставки')
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name']

    def __str__(self):
        return self.email
    

