from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Category, Item, Status, Order, Order_item

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'is_staff',)
    ordering = ('email', 'is_staff',)
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
            'fields': ('email', 'password1', 'password2', 'first_name',
                       'last_name', 'middle_name', 'address'),
        })
    )

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug',)
    list_display_links = ('slug',)
    list_editable = ('name',)

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'display_categories',)
    list_filter = ('categories',)

    def display_categories(self, obj):
        return ",".join([c.name for c in obj.categories.all()])
    display_categories.short_description = "Категории"

class OrderItemInline(admin.TabularInline):
    model = Order_item
    extra = 0

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 
                    'created_at', 'updated_at',)
    list_filter = ('status', 'created_at', 'updated_at')
    inlines = [OrderItemInline]

@admin.register(Status)
class StatusAdmin(admin.ModelAdmin):
    list_display = ('name',)