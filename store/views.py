from django.shortcuts import get_object_or_404, render, redirect
from .models import Product,Cart,CartItem
from .forms import CustomUserCreationForm,CustomAuthenticationForm
from django.contrib.auth import login,logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login
from .models import Order, OrderItem,TemporaryCheckout
from django.db.models import Q
import stripe
from django.conf import settings
# Create your views here.
stripe.api_key = settings.STRIPE_SECRET_KEY



def home_view(request):
    user = request.user
    query = request.GET.get('q')  # Get search query from URL, e.g., ?q=cream
    if query:
        # Filter products by name or description
        products = Product.objects.filter(
            Q(name__icontains=query) | Q(description__icontains=query)
        )
    else:
        products = Product.objects.all().order_by('-created_at')
    return render(request,'home.html',{'user':user, 'products':products})


def product_detail_view(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'product_detail.html', {'product': product})

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    
    # Get or create the user's cart
    cart, created = Cart.objects.get_or_create(user=request.user)

    # Get or create the cart item
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart')


@login_required
def cart_view(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product')

    # Add individual totals
    for item in items:
        item.total_price = item.product.price * item.quantity

    total_price = cart.total_price()

    return render(request, 'cart.html', {
        'products': items,
        'total_price': total_price
    })

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # Save user to DB
            login(request, user)  # Log user in after registration
            return redirect('home')  # Redirect to home
    else:
        form = CustomUserCreationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')
    else:
        form = CustomAuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')

from django.views.decorators.http import require_POST

@require_POST
@login_required
def update_cart_quantity(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    action = request.POST.get('action')

    if action == 'increment':
        cart_item.quantity += 1
        cart_item.save()
    elif action == 'decrement':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            cart_item.delete()
        else:
            cart_item.save()
    elif action == 'remove':
        cart_item.delete()

    return redirect('cart')


@login_required
def checkout_view(request):
   if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
          # Save to DB instead of session
        TemporaryCheckout.objects.update_or_create(
            user=request.user,
            defaults={
                'name': name,
                'phone': phone,
                'address': address
            }
        )
        return redirect('start_payment')
   

   return render(request,'checkout.html')

@login_required
def start_payment(request):
    cart = Cart.objects.get(user=request.user)
    cart_items = cart.items.all()
    if not cart_items.exists():
        return redirect('cart')


    
    line_items = []
    for item in cart_items:
        line_items.append({
            'price_data': {
                'currency': 'pkr',
                'product_data': {'name': item.product.name},
                'unit_amount': int(item.product.price * 100),
            },
            'quantity': item.quantity,
        })

    # Save shipping info temporarily
    name=request.POST.get('name')
    phone = request.POST.get('phone')
    address = request.POST.get('address')
    

    session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=request.build_absolute_uri('/payment/success/'),
        cancel_url=request.build_absolute_uri('/payment/cancel/'),
        metadata={'user_id': request.user.id}
    )

    return redirect(session.url, code=303)

@login_required
def payment_success(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_items = cart.items.all() 

    if not cart_items:
        return redirect('cart')
    
    try:
        temp_data = TemporaryCheckout.objects.get(user=request.user)
    except TemporaryCheckout.DoesNotExist:
        return redirect('checkout')

    # Save the order
    order = Order.objects.create(
        user=request.user,
        name=temp_data.name,
        phone=temp_data.phone,
        address=temp_data.address
    )

    for item in cart_items:
        
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity
        )
    cart.items.all().delete()  # Clear cart after order
    
    return render(request, 'payment_success.html', {'order': order})

@login_required
def payment_cancel(request):
    return render(request, 'payment_cancel.html')


def order_success(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    items = cart.items.select_related('product')

    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        address = request.POST.get('address')

        if name and phone and address:
            order = Order.objects.create(
                user=request.user,
                name=name,
                phone=phone,
                address=address
            )

            for item in items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity
                )

            cart.items.all().delete()  # Clear cart after order
            
    return render(request, 'order_success.html')


@login_required
def my_orders_view(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'my_orders.html', {'orders': orders})
