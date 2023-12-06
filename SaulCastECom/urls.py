from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('logout/', views.logout_view, name='logout'),
    path('products/', views.product_view, name='product'),
    path('cart/', views.cart_view, name='cart'),
    path('add_to_cart/<int:podcast_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove_from_cart/<int:podcast_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('update_cart/<int:podcast_id>/', views.update_cart, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('paymentwall-widget/<int:podcast_id>/<str:email>/', views.paymentwall_widget, name='paymentwall_widget'),
    path('paymentwall/pingback/', views.paymentwall_pingback, name='paymentwall_pingback'),
    # Add more URL patterns as needed
]
