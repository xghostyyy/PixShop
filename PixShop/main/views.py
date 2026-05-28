from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Item, Order, Order_item, Status

def item_list(request):
    items = Item.objects.all()
    return render(request, 'main/index.html', {'items': items})

def item_detail(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    return render(request, 'main/item_detail.html', {'item': item})

def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    cart = request.session.get('cart', {})

    cart[str(item_id)] = cart.get(str(item_id), 0) + 1
    request.session['cart'] = cart
    return redirect('item_list')

def cart_detail(request):
    cart = request.session.get('cart', {})
    items = Item.objects.filter(id__in =cart.keys())

    cart_items = []
    total = 0
    for item in items:
        qty = cart[str(item.id)]
        subtotal = item.price * qty
        total += subtotal
        cart_items.append({
            'item': item,
            'quantity': qty,
            'subtotal': subtotal,
        })

    return render(request, 'main/cart_detail.html', {
        'cart_items': cart_items,
        'total': total
    })

@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('item_lsit')
    items = Item.objects.filter(id__in=cart.keys())
    if not items.exists():
        return redirect('item_list')
    status_new, _ = Status.objects.get_or_create(
        code='new', defaults={'name': 'Новый'}
    )

    order = Order.objects.create(user=request.user, status=status_new)
    for item in items:
        qty = cart[str(item.id)]
        Order_item.objects.create(
            order=order,
            item=item,
            quantity=qty,
            price=item.price
        )
    order.update_total()
    request.session['cart'] = {}
    return redirect('order_conf', order_id=order.id)
    
def order_conf(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'main/order_conf.html', {'order', order})