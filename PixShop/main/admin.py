from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count, Sum
from django.utils.html import format_html

from .models import User, Category, Item, ItemImage, Status, Order, Order_item


# ── Брендинг панели ───────────────────────────────────────────────
admin.site.site_header = 'PIXSHOP'
admin.site.site_title = 'PixShop — панель управления'
admin.site.index_title = 'Управление магазином'


def _thumb(url, size=46):
    """Маленькое превью изображения для списков и форм."""
    return format_html(
        '<img src="{}" style="width:{}px;height:{}px;object-fit:cover;'
        'border:2px solid var(--border-color);image-rendering:pixelated;" />',
        url, size, size,
    )


# ── Пользователи ──────────────────────────────────────────────────
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'orders_count', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('email', 'first_name', 'last_name', 'adress')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Личная информация', {'fields': ('first_name', 'last_name',
                                          'middle_name', 'adress')}),
        ('Разрешения', {'fields': ('is_active', 'is_staff', 'is_superuser',
                                   'groups', 'user_permissions')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2',
                       'first_name', 'last_name', 'middle_name', 'adress'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_orders=Count('orders'))

    @admin.display(description='Заказов', ordering='_orders')
    def orders_count(self, obj):
        return obj._orders


# ── Категории ─────────────────────────────────────────────────────
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'items_count')
    list_display_links = ('name',)
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_items=Count('items'))

    @admin.display(description='Товаров', ordering='_items')
    def items_count(self, obj):
        return obj._items


# ── Товары ────────────────────────────────────────────────────────
class ItemImageInline(admin.TabularInline):
    model = ItemImage
    extra = 1
    fields = ('preview', 'image', 'order')
    readonly_fields = ('preview',)

    @admin.display(description='Превью')
    def preview(self, obj):
        if obj.image:
            return _thumb(obj.image.url, 60)
        return '—'


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('thumb', 'name', 'price', 'quantity',
                    'stock_badge', 'available', 'display_categories')
    list_display_links = ('thumb', 'name')
    list_filter = ('available', 'categories')
    list_editable = ('available', 'quantity')
    list_per_page = 25
    search_fields = ('name', 'description')
    autocomplete_fields = ('categories',)
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('image_preview',)
    inlines = [ItemImageInline]
    fieldsets = (
        ('Основное', {'fields': ('name', 'slug', 'description')}),
        ('Цена и склад', {'fields': ('price', 'quantity', 'available')}),
        ('Категории', {'fields': ('categories',)}),
        ('Главное изображение', {'fields': ('image', 'image_preview')}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')

    @admin.display(description='')
    def thumb(self, obj):
        if obj.image:
            return _thumb(obj.image.url)
        return format_html(
            '<span style="display:inline-flex;width:46px;height:46px;'
            'align-items:center;justify-content:center;border:2px dashed '
            'var(--border-color);font-size:9px;color:var(--body-quiet-color);">—</span>'
        )

    @admin.display(description='Изображение')
    def image_preview(self, obj):
        if obj.image:
            return _thumb(obj.image.url, 180)
        return 'Изображение не загружено'

    @admin.display(description='Наличие')
    def stock_badge(self, obj):
        if obj.quantity == 0:
            color, label = '#e63946', 'НЕТ'
        elif obj.quantity <= 3:
            color, label = '#facc15', f'МАЛО · {obj.quantity}'
        else:
            color, label = '#4ade80', f'OK · {obj.quantity}'
        return format_html(
            '<span style="font:700 10px/1 monospace;color:{0};border:1px solid {0};'
            'padding:3px 7px;border-radius:0;white-space:nowrap;">{1}</span>',
            color, label,
        )

    @admin.display(description='Категории')
    def display_categories(self, obj):
        return ', '.join(c.name for c in obj.categories.all()) or '—'


# ── Статусы ───────────────────────────────────────────────────────
@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name', 'orders_count')
    search_fields = ('name',)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_orders=Count('order'))

    @admin.display(description='Заказов', ordering='_orders')
    def orders_count(self, obj):
        return obj._orders


# ── Заказы ────────────────────────────────────────────────────────
class OrderItemInline(admin.TabularInline):
    model = Order_item
    extra = 0
    autocomplete_fields = ('item',)
    fields = ('item', 'quantity', 'price', 'subtotal')
    readonly_fields = ('subtotal',)

    @admin.display(description='Сумма')
    def subtotal(self, obj):
        if obj.pk:
            return format_html('<b>{} ₽</b>', obj.price * obj.quantity)
        return '—'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status_badge', 'positions',
                    'total_price', 'created_at')
    list_display_links = ('id', 'user')
    list_filter = ('status', 'created_at')
    search_fields = ('id', 'user__email', 'user__first_name', 'user__last_name')
    date_hierarchy = 'created_at'
    list_per_page = 30
    readonly_fields = ('created_at', 'updated_at', 'total_price')
    autocomplete_fields = ('user',)
    inlines = [OrderItemInline]
    fields = ('user', 'status', 'total_price', 'created_at', 'updated_at')

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('user', 'status')
            .annotate(_positions=Count('items'))
        )

    @admin.display(description='Позиций', ordering='_positions')
    def positions(self, obj):
        return obj._positions

    @admin.display(description='Статус', ordering='status')
    def status_badge(self, obj):
        palette = {
            'Новый': '#facc15',
            'Оплачен': '#6b8cff',
            'В доставке': '#38bdf8',
            'Завершен': '#4ade80',
            'Выполнен': '#4ade80',
            'Отменён': '#e63946',
        }
        name = obj.status.name if obj.status else '—'
        color = palette.get(name, '#7777aa')
        return format_html(
            '<span style="font:700 10px/1 monospace;color:{0};border:1px solid {0};'
            'padding:3px 8px;white-space:nowrap;">{1}</span>',
            color, name.upper(),
        )
