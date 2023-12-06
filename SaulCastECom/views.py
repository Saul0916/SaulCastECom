from django.shortcuts import render,redirect,get_object_or_404,redirect,HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm,AuthenticationForm
from django.contrib.auth import authenticate,login,logout
from .forms import LoginForm
from django.http import JsonResponse
from .models import Podcast,Cart,CartItem
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum,F,DecimalField
from django.http import HttpResponseBadRequest

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        username = request.user.username
        return render(request,'index.html',{'username':username})
    return render(request,'index.html')

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')  # Redirect to the 'index' page after successful login
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def checkout_view(request):
    # Handle checkout form submission and payment process
    return render(request,'checkout.html')

def product_view(request):
    podcasts = Podcast.objects.all()
    cart_items_count = CartItem.objects.filter(cart__user=request.user).aggregate(total_items=Sum('quantity'))['total_items'] or 0  # Get cart items count for the current user
    cart_items = CartItem.objects.filter(cart__user=request.user).select_related('podcast')
    items_info = cart_items.annotate(
        total_price=Sum(F('podcast__price') * F('quantity'), output_field=DecimalField())
    ).order_by('podcast__title').values('podcast__title', 'quantity', 'total_price')
    total_price_all_items = sum(float(item['total_price']) for item in items_info)
    context = {
        # Other context data
        'cart_items_count': cart_items_count,
        'podcasts': podcasts,
        'items_info': items_info,
        'total_price_all_items': total_price_all_items,
    }
    return render(request,'product.html',context)

def cart_view(request):
    # Retrieve cart items and quantities from the session (or your cart storage)

    # For example, assuming the cart is stored in the user's session
    if 'cart' in request.session:
        cart_items = request.session['cart']
    else:
        cart_items = {}

    # Process cart items to calculate total prices
    total_price = 0

    for name, item in cart_items.items():
        quantity = item.get('quantity', 0)
        price = item.get('price', 0)
        total_price += quantity * price
        # Add quantity information to each cart item
        item['total_price'] = quantity * price

    return render(request, 'cart.html', {'cart_items': cart_items.values(), 'total_price': total_price})

@login_required
def add_to_cart(request, podcast_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        podcast = get_object_or_404(Podcast, id=podcast_id)
        
        # Retrieve or create the user's cart (this can vary based on your implementation)
        cart, created = Cart.objects.get_or_create(user=request.user)  # Replace with your cart retrieval login

        # Calculate total cost for the cart
        cart_items = CartItem.objects.filter(cart=cart)
        total_cost = sum(item.total_price() for item in cart_items)

        messages.success(request, f"{quantity} {podcast.title}(s) added to cart.")
        return redirect('product')  # Redirect to the product page
    return redirect('product')  # Redirect to the product page if not a POST request

@login_required
def remove_from_cart(request, podcast_id):
    # Retrieve the cart item from the database based on the podcast ID
    cart_item = get_object_or_404(CartItem, podcast_id=podcast_id)
    quantity = int(request.POST.get('quantity', 0))
    # Ensure the cart item belongs to the current user
    if cart_item.cart.user != request.user:
        return HttpResponse("Unauthorized", status=401)

    # Decrease the quantity in the cart item
    if cart_item.quantity > 0:
        cart_item.quantity -= quantity
        cart_item.save()
    elif quantity > cart_item.quantity:
        return HttpResponseBadRequest("Requested quantity exceeds items in cart")
    else:
        # Remove the item from the cart if the quantity is 0 or less
        cart_item.delete()

    return redirect('product')  # Redirect back to the product view

@login_required
def update_cart(request, podcast_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 0))
        podcast = get_object_or_404(Podcast, id=podcast_id)
        cart, created = Cart.objects.get_or_create(user=request.user)

        if 'add_to_cart' in request.POST:
            cart_item, created = CartItem.objects.get_or_create(cart=cart, podcast=podcast)
            cart_item.quantity += quantity
            cart_item.save()
            messages.success(request, f"{quantity} {podcast.title}(s) added to cart.")
        elif 'remove_from_cart' in request.POST:
            try:
                cart_item = CartItem.objects.get(cart=cart, podcast=podcast)
                if cart_item.quantity <= 0:
                    messages.warning(request, f"{podcast.title} is already not in the cart.")
                else:
                    cart_item.quantity -= quantity
                    if cart_item.quantity <= 0:
                        cart_item.delete()
                        messages.success(request, f"{podcast.title} removed from cart.")
                    else:
                        cart_item.save()
                        messages.success(request, f"{quantity} {podcast.title}(s) removed from cart.")
            except CartItem.DoesNotExist:
                messages.warning(request,  f"Error: {podcast.title} is not in the cart!")

        return redirect('product')  # Redirect to the product page
