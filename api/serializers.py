from rest_framework import serializers
from .models import Restaurant, Category, MenuItem
from django.contrib.auth import get_user_model

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ['id', 'username', 'password', "email", "is_resturaunt"]

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)  # hash password
        user.save()
        return user
    

class MenuItemSerializer(serializers.ModelSerializer):
    class Meta:
        model= MenuItem
        fields = "__all__"
        read_only_fields = ['category']

class CategorySerializer(serializers.ModelSerializer):
    items = MenuItemSerializer(many=True, source='menu_item', read_only=True)
    class Meta:
        model = Category
        fields = ['name','id', 'is_active',"restaurant", 'items']
        read_only_fields = ['restaurant']
    

class RestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurant
        fields = '__all__'
        read_only_fields = ['owner', 'qr_code', 'created_at', 'updated_at']

class PublicRestaurantSerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, source='category')
    class Meta:
        model= Restaurant
        fields =['id','name','description', 'qr_code', 'slug','adress', 'phone', 'website', 'categories']

