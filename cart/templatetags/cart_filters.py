
from django import template

register = template.Library()

@register.filter(name='get_quantity')
def get_cart_quantity(cart, movie_id):
    """Get quantity for a movie from cart, handling both string and int movie_id"""
    if not cart or not movie_id:
        return 0
    
    try:
        # Try string key first
        return cart[str(movie_id)]
    except (KeyError, TypeError):
        # If not found, try integer key
        try:
            return cart[int(movie_id)]
        except (KeyError, ValueError, TypeError):
            return 0

@register.filter(name='multiply')
def multiply(value, arg):
    """Multiply value by arg"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0
