from django.urls import path
from . import views

urlpatterns = [
    # Главная
    path('', views.item_list, name='item_list'),

    # Товары
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('catalog/', views.catalog, name='catalog'),

    # Корзина
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('update-cart/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('update-cart-ajax/', views.update_cart_ajax, name='update_cart_ajax'),
    path('api/cart-count/', views.cart_count_api, name='cart_count_api'),

    # Заказ
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>/', views.order_conf, name='order_conf'),

    # Профиль (одна вьюха, две формы внутри)
    path('profile/', views.profile, name='profile'),
]