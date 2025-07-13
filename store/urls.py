from django.contrib import admin
from django.urls import path
from store import views

urlpatterns = [
    path('',views.home_view,name='home'),
    path('product/<int:pk>/', views.product_detail_view, name='product_detail'),
    path('cart/', views.cart_view, name='cart'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('update-cart/<int:pk>/', views.update_cart_quantity, name='update_cart'),
    path('checkout/', views.checkout_view, name='checkout'),
    path('order-success/', views.order_success, name='order_success'),
    path('my-orders/', views.my_orders_view, name='my_orders'),
    path('startpayment/',views.start_payment,name="start_payment"),
    path('payment/success/', views.payment_success, name='payment_success'),
    path('payment/cancel/', views.payment_cancel, name='payment_cancel'),




    
]