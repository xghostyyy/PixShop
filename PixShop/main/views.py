import json
from django.contrib import messages
from django.contrib.auth import login, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from .forms import PixPasswordChangeForm, ProfileUpdateForm, UserRegisterForm
from .models import Category, Item, Order, Order_item, Status


#  ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ

def _get_cart(request):
    return request.session.get('cart', {})


def _save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


def _cart_items_with_totals(cart):
    if not cart:
        return [], 0

    items = (
        Item.objects
        .filter(id__in=cart.keys(), available=True)
        .prefetch_related('categories')
    )

    entries = []
    total = 0
    for item in items:
        qty = cart[str(item.id)]
        subtotal = item.price * qty
        total += subtotal
        entries.append({'item': item, 'quantity': qty, 'subtotal': subtotal})

    return entries, total


#  КАТАЛОГ / ТОВАРЫ

def item_list(request):
    items = (
        Item.objects
        .filter(available=True)
        .prefetch_related('categories')
    )
    return render(request, 'main/index.html', {'items': items})


def item_detail(request, item_id):
    item = get_object_or_404(
        Item.objects.prefetch_related('categories'),
        id=item_id,
        available=True,
    )
    return render(request, 'main/item_detail.html', {'item': item})


def catalog(request):
    SORT_MAP = {
        'name_asc':   'name',
        'name_desc':  '-name',
        'price_asc':  'price',
        'price_desc': '-price',
        'newest':     '-id', 
    }

    categories = Category.objects.all()
    selected_category = request.GET.get('category', '')
    sort = request.GET.get('sort', 'name_asc')

    items = Item.objects.filter(available=True).prefetch_related('categories')

    if selected_category:
        items = items.filter(categories__id=selected_category).distinct()

    order_by = SORT_MAP.get(sort, 'name')
    items = items.order_by(order_by)

    return render(request, 'main/catalog.html', {
        'items': items,
        'categories': categories,
        'selected_category': selected_category,
        'sort': sort,
    })


#  КОРЗИНА

def add_to_cart(request, item_id):
    item = get_object_or_404(Item, id=item_id, available=True)
    cart = _get_cart(request)

    current_qty = cart.get(str(item_id), 0)

    # Проверка складского остатка
    if current_qty >= item.quantity:
        messages.error(
            request,
            f'Товар «{item.name}» недоступен в нужном количестве. '
            f'На складе: {item.quantity} шт.'
        )
        # Возвращаем на страницу, с которой пришли, или на каталог
        return redirect(request.META.get('HTTP_REFERER', 'catalog'))

    cart[str(item_id)] = current_qty + 1
    _save_cart(request, cart)

    messages.success(request, f'«{item.name}» добавлен в корзину.')
    return redirect(request.META.get('HTTP_REFERER', 'catalog'))


def cart_detail(request):
    cart = _get_cart(request)
    cart_items, total = _cart_items_with_totals(cart)
    return render(request, 'main/cart_detail.html', {
        'cart_items': cart_items,
        'total': total,
    })


def update_cart_item(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        cart = _get_cart(request)

        if quantity > 0:
            item = get_object_or_404(Item, id=item_id)
            # Не даём выставить больше, чем есть на складе
            quantity = min(quantity, item.quantity)
            cart[str(item_id)] = quantity
        else:
            cart.pop(str(item_id), None)

        _save_cart(request, cart)
    return redirect('cart_detail')


def update_cart_ajax(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Метод не разрешён'}, status=405)

    if request.headers.get('x-requested-with') != 'XMLHttpRequest':
        return JsonResponse({'success': False, 'error': 'Не AJAX-запрос'}, status=400)

    try:
        data = json.loads(request.body)
        item_id = str(data['item_id'])
        quantity = int(data['quantity'])
    except (KeyError, ValueError, json.JSONDecodeError):
        return JsonResponse({'success': False, 'error': 'Неверные данные'}, status=400)

    cart = _get_cart(request)

    if quantity > 0:
        try:
            item = Item.objects.get(id=item_id, available=True)
        except Item.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Товар не найден'}, status=404)

        if quantity > item.quantity:
            return JsonResponse({
                'success': False,
                'error': f'На складе только {item.quantity} шт.',
            }, status=400)

        cart[item_id] = quantity
    else:
        cart.pop(item_id, None)

    _save_cart(request, cart)

    items_qs = Item.objects.filter(id__in=cart.keys(), available=True)
    total = sum(item.price * cart[str(item.id)] for item in items_qs)
    new_subtotal = 0
    for item in items_qs:
        if str(item.id) == item_id:
            new_subtotal = item.price * cart.get(item_id, 0)
            break

    return JsonResponse({
        'success': True,
        'new_subtotal': float(new_subtotal),
        'new_total': float(total),
    })


def cart_count_api(request):
    cart = _get_cart(request)
    return JsonResponse({'count': sum(cart.values())})


#  ОФОРМЛЕНИЕ ЗАКАЗА

@login_required
def checkout(request):
    cart = _get_cart(request)
    if not cart:
        messages.error(request, 'Корзина пуста.')
        return redirect('cart_detail')

    items = list(
        Item.objects
        .filter(id__in=cart.keys(), available=True)
        .select_for_update()   
    )

    if not items:
        messages.error(request, 'Все товары в корзине недоступны.')
        _save_cart(request, {})
        return redirect('catalog')

    # Проверка остатков
    errors = []
    for item in items:
        needed = cart[str(item.id)]
        if item.quantity < needed:
            errors.append(
                f'«{item.name}»: нужно {needed} шт., на складе {item.quantity} шт.'
            )

    if errors:
        for err in errors:
            messages.error(request, err)
        return redirect('cart_detail')

    # Создаём заказ 
    from django.db import transaction

    status_new, _ = Status.objects.get_or_create(name='Новый')

    with transaction.atomic():
        order = Order.objects.create(user=request.user, status=status_new)

        for item in items:
            qty = cart[str(item.id)]
            Order_item.objects.create(
                order=order,
                item=item,
                quantity=qty,
                price=item.price,
            )
            # Списываем со склада
            item.quantity -= qty
            # Если товара не осталось — скрываем его
            if item.quantity <= 0:
                item.quantity = 0
                item.available = False
            item.save(update_fields=['quantity', 'available'])

        order.update_total()

    _save_cart(request, {})
    messages.success(request, f'Заказ №{order.id} успешно оформлен!')
    return redirect('order_conf', order_id=order.id)


def order_conf(request, order_id):
    order = get_object_or_404(
        Order.objects.select_related('status', 'user')
                     .prefetch_related('items__item'),
        id=order_id,
    )
    return render(request, 'main/order_conf.html', {'order': order})


#  ПРОФИЛЬ

@login_required
def profile(request):
    user = request.user
    profile_form = ProfileUpdateForm(instance=user)
    password_form = PixPasswordChangeForm(user=user)

    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'profile':
            profile_form = ProfileUpdateForm(request.POST, instance=user)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, 'Данные профиля обновлены.')
                return redirect('profile')
            # форма невалидна — отобразим с ошибками

        elif form_type == 'password':
            password_form = PixPasswordChangeForm(user=user, data=request.POST)
            if password_form.is_valid():
                password_form.save()
                # Обновляем хэш сессии, чтобы пользователь не вылетел
                update_session_auth_hash(request, password_form.user)
                messages.success(request, 'Пароль успешно изменён.')
                return redirect('profile')
            # форма невалидна — отобразим с ошибками

    orders = (
        user.orders
        .select_related('status')
        .prefetch_related('items__item')
        .order_by('-created_at')
    )

    return render(request, 'main/profile.html', {
        'profile_form': profile_form,
        'password_form': password_form,
        'orders': orders,
    })


#  РЕГИСТРАЦИЯ

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Добро пожаловать в PixShop!')
            return redirect('item_list')
    else:
        form = UserRegisterForm()
    return render(request, 'main/register.html', {'form': form})