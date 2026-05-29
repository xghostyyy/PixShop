from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email обязателен')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True, 
                              verbose_name='Электронная почта')
    middle_name = models.CharField(max_length=100, blank=True, 
                              verbose_name='Отчество')
    adress = models.CharField(max_length=100, 
                              verbose_name='Адрес доставки')
    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

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

    slug = models.SlugField(max_length=100, unique=True)
    
    class Meta:
        verbose_name = 'Товар'
        verbose_name_plural = 'Товары'
        ordering = ('name', 'price',)

    def __str__(self):
        return self.name

class Status(models.Model):
    name = models.CharField(max_length=100, db_index=True,
                             verbose_name='Название статуса')
    class Meta:
        verbose_name = 'Статус'
        verbose_name_plural = 'Статусы'
        ordering = ('pk',)

    def __str__(self):
        return self.name
    
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders',
                             verbose_name='Пользователь')
    status = models.ForeignKey(Status, on_delete=models.SET_DEFAULT, default=1, 
                               verbose_name='Статус')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Дата обновления')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0,
                                      verbose_name='Общая сумма')
    
    class Meta:
        verbose_name = 'Заказ'
        verbose_name_plural = 'Заказы'
        ordering = ('created_at', 'updated_at', 'total_price', 'user', 'status',)

    def update_total(self):
        self.total_price = sum(item.price * item.quantity for item in 
                               self.items.all())
        self.save()

class Order_item(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        verbose_name  = 'Позиция заказа'
        verbose_name_plural = 'Позиция заказов'
        unique_together = ('order', 'item',)

    def __str__(self):
        return f'{self.quantity} x {self.item.name} (заказ {self.order_id})'
    

