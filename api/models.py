from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import qrcode
from io import BytesIO
from django.core.files import File
from django.utils import  timezone

class User(AbstractUser):
    is_resturaunt = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class Restaurant(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="restaurant")
    description = models.TextField(null=True , blank=True)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, null=True)
    adress = models.TextField(null=True, blank=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to="restaurant_logos/", blank=True, null=True)
    qr_code = models.ImageField(upload_to='qr_codes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.qr_code:
            qr = qrcode.make(f"http://localhost:5173/menu/{self.slug}")
            buffer = BytesIO()
            qr.save(buffer, format='PNG')
            file_name = f"qr_{self.slug}.png"
            self.qr_code.save(file_name, File(buffer), save=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    

    

class Category(models.Model):
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='category')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} id:{self.id} for {self.restaurant.name} id:{self.restaurant.id}"

class MenuItem(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_item')
    name = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to="menu-items/", blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
    


class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart', null=True, blank=True)
    session_key = models.CharField(max_length=40, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.user:
            return f"Cart of {self.user.username}"
        else:
            return f"cart of {self.session_key}"
    
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='cart_item')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='cart_item')
    quantity = models.PositiveIntegerField(default=1)
    

    def __str__(self):
        return f"{self.menu_item.name} * {self.quantity}"
    
    def total_price(self):
        return self.menu_item.price * self.quantity
    
    @property
    def restaurant(self):
        return self.menu_item.category.restaurant
    

class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("preparing", "Preparing"),
        ("ready", "Ready for Pickup"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="orders")
    restaurant = models.ForeignKey("Restaurant", on_delete=models.CASCADE)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    customer_name = models.CharField(max_length=255)
    customer_phone = models.CharField(max_length=50)
    delivery_address = models.TextField(blank=True, null=True)  # Optional for takeout

    def __str__(self):
        return f"Order #{self.id} - {self.restaurant.name} - {self.status}"
    
    @property
    def formatted_updated_at(self):
        return self.updated_at.strftime("%d %b %Y") 
    

    

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.menu_item.name} x {self.quantity}"

    @property
    def total_price(self):
        return self.price * self.quantity


class Payment(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name="payment")
    payment_method = models.CharField(max_length=50)  # e.g. "card", "cash"
    payment_status = models.CharField(max_length=20, default="pending")
    transaction_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for Order #{self.order.id} - {self.payment_status}"




