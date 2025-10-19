
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from movies.models import Movie
from .utils import calculate_cart_total
from .models import Order, Item
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import random

def index(request):
    cart_total = 0
    movies_in_cart = []
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())
    if (movie_ids != []):
        movies_in_cart = Movie.objects.filter(id__in=movie_ids)
        cart_total = calculate_cart_total(cart, movies_in_cart)

    template_data = {}
    template_data['title'] = 'Cart'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    return render(request, 'cart/index.html', {'template_data': template_data})

def add(request, id):
    get_object_or_404(Movie, id=id)
    cart = request.session.get('cart', {})
    cart[id] = request.POST['quantity']
    request.session['cart'] = cart
    return redirect('cart.index')

def clear(request):
    request.session['cart'] = {}
    return redirect('cart.index')

@login_required
def checkout(request):
    """Show checkout form for location input"""
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    if (movie_ids == []):
        return redirect('cart.index')
    
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)

    template_data = {}
    template_data['title'] = 'Checkout'
    template_data['movies_in_cart'] = movies_in_cart
    template_data['cart_total'] = cart_total
    
    return render(request, 'cart/checkout.html', {'template_data': template_data})

@login_required
def purchase(request):
    """Process the purchase with location data"""
    if request.method != 'POST':
        return redirect('cart.checkout')
    
    cart = request.session.get('cart', {})
    movie_ids = list(cart.keys())

    if (movie_ids == []):
        return redirect('cart.index')
    
    # Get location data from form
    state = request.POST.get('state', '').strip()
    city = request.POST.get('city', '').strip()
    
    if not state:
        messages.error(request, 'Please select your state.')
        return redirect('cart.checkout')
    
    movies_in_cart = Movie.objects.filter(id__in=movie_ids)
    cart_total = calculate_cart_total(cart, movies_in_cart)
    
    # Create order with user-provided location
    order = Order()
    order.user = request.user
    order.total = cart_total
    order.state = state
    order.save()

    for movie in movies_in_cart:
        item = Item()
        item.movie = movie
        item.price = movie.price
        item.order = order
        item.quantity = cart[str(movie.id)]
        item.save()

    request.session['cart'] = {}
    messages.success(request, f'Purchase completed! Order #{order.id} from {city}, {state}')
    
    template_data = {}
    template_data['title'] = 'Purchase confirmation'
    template_data['order_id'] = order.id
    template_data['state'] = state
    template_data['city'] = city
    return render(request, 'cart/purchase.html', {'template_data': template_data})
