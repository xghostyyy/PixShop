from django.urls import path
from . import views

urlpatterns = [
    path('', views.item_list, name='item_list'),
    path('item/<int:item_id>/', views.item_detail, name='item_detail'),
    path('add-to-cart/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_detail, name='cart_detail'),
    path('checkout/', views.checkout, name='checkout'),
    path('order/<int:order_id>', views.order_conf, name='order_conf'),
    path('update-cart/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('profile/', views.profile, name='profile'),
    path('update-cart-ajax/', views.update_cart_ajax, name='update_cart_ajax'),
]