from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from . import views


urlpatterns = [
    path("users/register/", views.UserListCreateView.as_view(), name='register-user'),
    path("users/login/", TokenObtainPairView.as_view(), name='login'),
    path('users/token/refresh', TokenRefreshView.as_view(), name='refresh-token'),
    path('users/logout/', views.LogoutView.as_view(), name='logout'),
    #Restaurants
    path('restaurants/', views.RestaurantListCreateView.as_view(), name='register-restaurant'),
    path('restaurants/<int:pk>/', views.RestaurantDetailView.as_view(), name='restaurant-detail'),
    #Categories
    path('restaurants/<int:pk>/categories/', views.CategoryView.as_view(), name='categories'),
    path('restaurants/<int:pk>/categories/<int:category_pk>/', views.CategoryDetailsView.as_view(), name='categories-detail'),
    #Menu
    path('restaurants/<int:pk>/categories/<int:category_pk>/menuitems/', views.MenuItemView.as_view(), name='menu-items'),
    path('restaurants/<int:pk>/categories/<int:category_pk>/menuitems/<int:menuitem_pk>/', views.MenuDetailsView.as_view(), name='menu-items-detail'),
    #Public Views
    path('<slug:slug>/', views.PublicRestaurantView.as_view(), name='public-menu'),
    path('public/restaurants/', views.PublicAllRestaurantsView.as_view(), name='restaurant-public')

    # path('restaurant/category/', views.CategoryView.as_view(), name='category'),
    # path('restaurant/menu', views.MenuItemView.as_view(), name='menu')
]