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
    

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, 
                            verbose_name='Название', db_index=True)
    slug = models.SlugField(max_length=100, unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name

class Item(models.Model):
    name = models.CharField(max_length=100, db_index=True,
                            verbose_name='Название товара')
    description = models.TextField(blank = True, verbose_name='Описание')
    price = models.DecimalField(max_digits=10, decimal_places=2, 
                                verbose_name='Цена')
    image = models.ImageField(upload_to='items/', blank=True, null=True,
                              verbose_name='Изображение товара')
    categories = models.ManyToManyField(Category, related_name='items', 
                                        verbose_name='Категории')
    available = models.BooleanField(default=True, verbose_name='Видимость')
    quantity = models.IntegerField(default=1, verbose_name='Количество товара')
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name', 'price', 'categories',)

    def __str__(self):
        return self.name
