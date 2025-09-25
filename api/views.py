from django.shortcuts import render, get_object_or_404
from django.contrib.auth import get_user_model
from .models import Restaurant, Category, MenuItem, Cart, CartItem, Order, OrderItem
from .serializers import UserSerializer, RestaurantSerializer, CategorySerializer, MenuItemSerializer,OrderItemSerializer, OrderSerializer, PublicRestaurantSerializer, CartSerializer, CartItemSerializer
from rest_framework import generics,status, permissions
from rest_framework.views import APIView, Response
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
import logging
logger = logging.getLogger(__name__)

    #User Related Views
User = get_user_model()
class UserListCreateView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors)
    
class LogoutView(APIView):
    def post(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return Response({"detail": "Refresh token is required."}, 
                            status=status.HTTP_400_BAD_REQUEST)
        try:
            token = RefreshToken(refresh_token)
            token.blacklist()  # Blacklist refresh token so it can't be used again
            return Response({"detail": "Successfully logged out."}, 
                            status=status.HTTP_205_RESET_CONTENT)
        except TokenError:
            return Response({"detail": "Invalid or expired token."}, 
                            status=status.HTTP_400_BAD_REQUEST)
    

#Restaurnat Related Views
class RestaurantListCreateView(generics.GenericAPIView):
    serializer_class = RestaurantSerializer
    permission_classes = [permissions.AllowAny]
    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)
    
    def get(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    def post(self,request):
        serializer= self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(owner=request.user)
        return Response(serializer.data)
    
class RestaurantDetailView(generics.GenericAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = RestaurantSerializer
    def get_queryset(self):
        return Restaurant.objects.filter(owner=self.request.user)

    def get_object(self):
        pk = self.kwargs.get("pk")
        return Restaurant.objects.get(owner=self.request.user, pk=pk)
    
    def get(self, request, pk):
        restaurant = self.get_object()
        serializer = self.get_serializer(restaurant)
        return Response(serializer.data)
    
    def put(self, request, pk):
        restaurant= self.get_object()
        serializer = self.get_serializer(restaurant, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        restaurant=self.get_object()
        serializer = self.get_serializer(restaurant, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request, pk):
        restaurant= self.get_object()
        if not restaurant:
            return Response({"detail": "Not Found"}, status=status.HTTP_404_NOT_FOUND)
        restaurant.delete()
        return Response({"detail": "Deleted Successfully"}, status=status.HTTP_204_NO_CONTENT)
    

#Category Related Views
class CategoryView(generics.GenericAPIView):
    serializer_class= CategorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        pk = self.kwargs.get("pk")
        return Category.objects.filter(restaurant=pk)

    def get(self,request, pk):
        category = self.get_queryset()
        serializer = CategorySerializer(category, many=True)
        return Response(serializer.data)
    
    def post(self, request, pk):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(restaurant_id=pk)
            return Response(serializer.data)
        return Response(serializer.errors)
    
class CategoryDetailsView(generics.GenericAPIView):
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        category_pk = self.kwargs.get('category_pk')
        return Category.objects.get(restaurant=pk, id=category_pk)
    
    def get(self, request, pk, category_pk):
        category = self.get_object()
        serializer = self.get_serializer(category)
        return Response(serializer.data)
    
    def put(self, request, pk, category_pk):
        category = self.get_object()
        serializer= self.get_serializer(category, data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
    
    def patch(self, request, pk , category_pk):
        category = self.get_object()
        serializer = self.get_serializer(category , data=request.data, partial= True)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request,pk , category_pk):
        category = self.get_object()
        category.delete()
        return Response({"detail": "Category deleted successfully."}, status=204)



#Menu Related Views    
class MenuItemView(generics.GenericAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        pk = self.kwargs.get('pk')
        category_pk = self.kwargs.get('category_pk')
        return MenuItem.objects.filter(category=category_pk)


    def get(self, request,pk, category_pk):
        items = self.get_queryset()
        serilaizer = MenuItemSerializer(items, many=True)
        return Response(serilaizer.data)
    
    def post(self, request, pk , category_pk):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(category_id=category_pk)
            return Response(serializer.data)
        return Response(serializer.errors)
    
class MenuDetailsView(generics.GenericAPIView):
    serializer_class = MenuItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        pk = self.kwargs.get('pk')
        category_pk = self.kwargs.get("category_pk")
        menuitem_pk = self.kwargs.get('menuitem_pk')
        return MenuItem.objects.get(category=category_pk, id=menuitem_pk)
    
    def get(self, request, pk, category_pk, menuitem_pk):
        item = self.get_object()
        serilaizer = self.get_serializer(item)
        return Response(serilaizer.data)
    
    def put(self, request, pk , category_pk, menuitem_pk):
        item= self.get_object()
        serializer = self.get_serializer(item, data=request.data)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
    
    def patch(self, request, pk , category_pk, menuitem_pk):
        item= self.get_object()
        serializer = self.get_serializer(item, data=request.data, partial = True)
        serializer.is_valid(raise_exception = True)
        serializer.save()
        return Response(serializer.data)
    
    def delete(self, request, pk , category_pk, menuitem_pk):
        item = self.get_object()
        item.delete()
        return Response({"detail": "Item deleted successfully."}, status=204)
    
    
class PublicRestaurantView(generics.RetrieveAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = PublicRestaurantSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = "slug"

    # def retrieve(self, request, *args, **kwargs):
    #     logger.info(f"PublicRestaurantView called | user={request.user} | headers={request.headers}")
    #     return super().retrieve(request, *args, **kwargs)

class PublicAllRestaurantsView(generics.ListAPIView):
    queryset = Restaurant.objects.all()
    serializer_class = PublicRestaurantSerializer
    permission_classes = [permissions.AllowAny]



def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart




class CartListView(generics.ListAPIView):
    serializer_class = CartSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)
    

class CartItemView(generics.GenericAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        """
        Add a new item to the cart (or increase quantity if it already exists).
        """
        cart = get_or_create_cart(request)
        menu_item_id = request.data.get("menu_item")
        quantity = int(request.data.get("quantity", 1))

        menu_item = get_object_or_404(MenuItem, id=menu_item_id)

        cart_item, created = CartItem.objects.get_or_create(
            cart=cart, menu_item=menu_item, defaults={"quantity": quantity}
        )

        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        return Response(
            {"message": "Item added to cart", "cart_item_id": cart_item.id},
            status=status.HTTP_201_CREATED
        )

    def patch(self, request, pk):
        """
        Update the quantity of a specific cart item.
        """
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=pk, cart=cart)

        quantity = request.data.get("quantity")
        if quantity is not None:
            cart_item.quantity = int(quantity)
            cart_item.save()

        return Response({"message": "Item updated successfully"})

    def delete(self, request, pk):
        """
        Remove a specific cart item.
        """
        cart = get_or_create_cart(request)
        cart_item = get_object_or_404(CartItem, id=pk, cart=cart)
        cart_item.delete()
        return Response({"message": "Item removed"}, status=status.HTTP_204_NO_CONTENT)
    


class CheckoutView(generics.GenericAPIView):
    serializer_class = OrderSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get(self, request):
        order = self.get_queryset()
        serializer = self.get_serializer(order, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save(user=request.user)
        Cart.objects.filter(user=request.user).delete()
        return Response (serializer.data)

