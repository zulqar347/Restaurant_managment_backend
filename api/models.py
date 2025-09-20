from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify
import qrcode
from io import BytesIO
from django.core.files import File

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
    
    



