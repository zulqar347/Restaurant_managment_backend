from django.contrib import admin
from .models import User, Restaurant, Category, MenuItem
from django.utils.html import format_html

# Register your models here.
# @admin.register(Restaurant)
# class ReastaurantAdmin(admin.ModelAdmin):
#     list_display = ['owner', 'name', 'slug', 'adress']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['username', 'password', "email", "is_resturaunt"]


# @admin.register(Category)
# class CategoryAdmin(admin.ModelAdmin):
#     list_display = ['restaurant', 'name',  'is_active']

# @admin.register(MenuItem)
# class MenuItemAdmin(admin.ModelAdmin):
#     list_display=['category', 'name', 'price', 'image', 'is_available']


class MenuItemInLine(admin.TabularInline):
    model = MenuItem
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ['restaurant', 'name',  'is_active']
    list_filter = ['restaurant',]
    inlines = [MenuItemInLine]


class CategoryInline(admin.TabularInline):
    model = Category
    extra = 1


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",) }
    list_display = ("name", "slug", "qr_code_preview")
    readonly_fields = ("qr_code",)
    inlines = [CategoryInline]  # show categories inline

    def qr_code_preview(self, obj):
        if obj.qr_code:
            return format_html(f'<img src="{obj.qr_code.url}" width="150" height="150" />')
        return "No QR code"

    qr_code_preview.short_description = "QR Code"

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    search_fields = ("name",)
    list_display = ("name", "category", "price")
    list_filter = ("category__restaurant",)