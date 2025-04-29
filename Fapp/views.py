from django.views import View
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.models import User
from django.contrib import messages
from .forms import SignUpForm, CheckoutForm, ContactForm
from .models import Product, Contact, Cart, CartItem, Order
import uuid



def home(request):
    return render(request, 'home.html' )


def login_user(request):    
	if request.method == "POST":
		username = request.POST['username']
		password = request.POST['password']
		#authenticate
		user = authenticate(request, username=username, password=password)
		if user is not None:
			login(request, user)
			messages.success(request, "You have Login Successfully!")
			return redirect('home')
		else:
			messages.success(request, "there was an error loggin in, please try again...")
			return redirect('login')
	else:
		return render(request, 'login.html', )

def logout_user(request):
	logout(request)
	messages.success(request, 'You Have Been Logged Out.....')
	return redirect('home')

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid:
        	form.save()
        return redirect('success')
    else:
        form = ContactForm()
    context = {'form':form}  
    return render(request, 'contact.html', context) 
        
def contact_success(request):
    return render(request, 'contact_success.html')       

def register_user(request):
	if request.method == "POST":
		form = SignUpForm(request.POST)
		if form.is_valid():
			form.save()
			#authenticate-&-login
			username = form.cleaned_data['username']
			password = form.cleaned_data['password1']
			user = authenticate(username=username, password=password)
			login(request, user)
			messages.success(request, "You Have Successfully Register! Welcome")
			return redirect('login')
	else:
		form = SignUpForm()    
		return render(request, 'register.html', {'form':form})

	return render(request, 'register.html', {'form':form})



def menu(request):
	product = Product.objects.all()
	return render(request, 'menu.html', {'product':product})

#CART
def get_or_create_cart(request):
    if request.user.is_authenticated:
        user = request.user
        carts = Cart.objects.filter(user=user)
        if carts.count() > 1:
            carts.exclude(id=carts.first().id).delete()
        cart, created = Cart.objects.get_or_create(user=request.user)
    else:
        if not request.session.session_key:
            request.session.create()
        session_key = request.session.session_key
        cart, created = Cart.objects.get_or_create(session_key=session_key)
    return cart

def add_to_cart(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = get_or_create_cart(request)
    
    # Check if product already in cart
    cart_item, created = CartItem.objects.get_or_create(
        cart=cart,
        product=product,
        defaults={'price': product.price}
    )
    
    if not created:
        cart_item.quantity += 1
        cart_item.save()
    
    messages.success(request, f"{product.name} added to your cart.")
    return redirect('cart_detail')

def cart_detail(request):
    user = request.user
    # carts = Cart.objects.filter(user=user)
    # if carts.count() > 1:
    #     carts.exclude(id=carts.first().id).delete()
    cart = get_or_create_cart(request)
    return render(request, 'cart_detail.html', {'cart': cart})


def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id)
    if request.user.is_authenticated and cart_item.cart.user != request.user:
        messages.error(request, "You don't have permission to remove this item.")
    else:
        cart_item.delete()
        messages.success(request, "Item removed from your cart.")
    return redirect('cart_detail')

def update_cart_item(request, item_id):
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        cart_item = get_object_or_404(CartItem, id=item_id)
        
        if request.user.is_authenticated and cart_item.cart.user != request.user:
            messages.error(request, "You don't have permission to update this item.")
        elif quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, "Cart updated successfully.")
        else:
            cart_item.delete()
            messages.success(request, "Item removed from your cart.")
    
    return redirect('cart_detail')


@login_required
def checkout(request):
    cart = get_or_create_cart(request)
    
    if not cart.items.exists():
        messages.warning(request, "Your cart is empty.")
        return redirect('cart_detail')
    
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            order = Order.objects.create(
                user=request.user,
                cart=cart,
                total_price=cart.get_total_price(),
                shipping_address=form.cleaned_data['shipping_address'],
                billing_address=form.cleaned_data['billing_address'],
                payment_method=form.cleaned_data['payment_method']
            )
            
            # Create a new cart for the user
            new_cart = Cart.objects.create(user=request.user)
            
            # Transfer session cart to user if they were anonymous
            if not request.user.is_authenticated and request.session.session_key:
                session_cart = Cart.objects.filter(session_key=request.session.session_key).first()
                if session_cart:
                    for item in session_cart.items.all():
                        item.cart = new_cart
                        item.save()
                    session_cart.delete()
            
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order_confirmation', order_id=order.id)
    else:
        initial_data = {}
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            profile = request.user.profile
            initial_data = {
                'shipping_address': profile.shipping_address,
                'billing_address': profile.billing_address,
            }
        form = CheckoutForm(initial=initial_data)
    
    return render(request, 'checkout.html', {
        'cart': cart,
        'form': form,
    })


@login_required
def order_confirmation(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'order_confirmation.html', {'order': order})

@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'order_history.html', {'orders': orders})