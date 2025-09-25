from rest_framework import serializers
from .models import Restaurant, Category, MenuItem, Order, OrderItem, Cart, CartItem
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
        fields = '__all__'
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



class CartItemSerializer(serializers.ModelSerializer):
    restaurant = serializers.SerializerMethodField()
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    class Meta:
        model = CartItem
        fields = ['id', 'menu_item','menu_item_name', 'quantity', "total_price", 'restaurant']

    def get_restaurant(self, obj):
        return obj.menu_item.category.restaurant.id

    
class CartSerializer(serializers.ModelSerializer):
    cart_item = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['id','user', 'session_key', 'created_at', 'cart_item']

class OrderItemSerializer(serializers.ModelSerializer):
    menu_item_name = serializers.CharField(source='menu_item.name', read_only=True)
    class Meta:
        model = OrderItem
        fields= ['id', 'quantity', 'price', 'total_price', 'menu_item', 'menu_item_name']
        read_only_fields = ['total_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    restaurant_name = serializers.CharField(source='restaurant.name',read_only=True)
    formatted_updated_at = serializers.ReadOnlyField()
    class Meta:
        model = Order
        fields = ['id', 'user', 'restaurant', 'restaurant_name','total_price','status', 
                  'created_at', 'updated_at','formatted_updated_at', 'items','customer_name',
                    'customer_phone', 'delivery_address']
        read_only_fields = ['user', 'status','created_at', 'updated_at']
        
    def create(self, validated_data):
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)
        order_items = [OrderItem(order=order, **item) for item in items_data]
        OrderItem.objects.bulk_create(order_items)
        return order
