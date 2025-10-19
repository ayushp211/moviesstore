
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.db.models import Count, Sum
from cart.models import Order, Item
from datetime import datetime, timedelta

def index(request):
    search_term = request.GET.get('search')
    if search_term:
        movies = Movie.objects.filter(name__icontains=search_term)
    else:
        movies = Movie.objects.all()

    template_data = {}
    template_data['title'] = 'Movies'
    template_data['movies'] = movies
    return render(request, 'movies/index.html', {'template_data': template_data})

def show(request, id):
    movie = Movie.objects.get(id=id)
    reviews = Review.objects.filter(movie=movie, reported=False)

    template_data = {}
    template_data['title'] = movie.name
    template_data['movie'] = movie
    template_data['reviews'] = reviews
    return render(request, 'movies/show.html', {'template_data': template_data})

@login_required
def create_review(request, id):
    if request.method == 'POST' and request.POST['comment'] != '':
        movie = Movie.objects.get(id=id)
        review = Review()
        review.comment = request.POST['comment']
        review.movie = movie
        review.user = request.user
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def edit_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.user != review.user:
        return redirect('movies.show', id=id)

    if request.method == 'GET':
        template_data = {}
        template_data['title'] = 'Edit Review'
        template_data['review'] = review
        return render(request, 'movies/edit_review.html', {'template_data': template_data})
    elif request.method == 'POST' and request.POST['comment'] != '':
        review = Review.objects.get(id=review_id)
        review.comment = request.POST['comment']
        review.save()
        return redirect('movies.show', id=id)
    else:
        return redirect('movies.show', id=id)

@login_required
def delete_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, user=request.user)
    review.delete()
    return redirect('movies.show', id=id)

@login_required
def report_review(request, id, review_id):
    review = get_object_or_404(Review, id=review_id, movie_id=id)
    if request.method == 'POST':
        review.reported = True
        review.save()
    return redirect('movies.show', id=id)

def petitions(request):
    petitions = Petition.objects.all().order_by('-created_date')
    
    # Add vote status for each petition if user is authenticated
    if request.user.is_authenticated:
        for petition in petitions:
            petition.user_has_voted = petition.has_user_voted(request.user)
    
    template_data = {}
    template_data['title'] = 'Movie Petitions'
    template_data['petitions'] = petitions
    return render(request, 'movies/petitions.html', {'template_data': template_data})

@login_required
def create_petition(request):
    if request.method == 'POST':
        movie_title = request.POST.get('movie_title', '').strip()
        description = request.POST.get('description', '').strip()
        
        if movie_title and description:
            petition = Petition()
            petition.movie_title = movie_title
            petition.description = description
            petition.created_by = request.user
            petition.save()
            messages.success(request, 'Petition created successfully!')
            return redirect('movies.petitions')
        else:
            messages.error(request, 'Please fill in all fields.')
    
    template_data = {}
    template_data['title'] = 'Create Petition'
    return render(request, 'movies/create_petition.html', {'template_data': template_data})

@login_required
def vote_petition(request, petition_id):
    petition = get_object_or_404(Petition, id=petition_id)
    
    if petition.has_user_voted(request.user):
        petition.votes.remove(request.user)
        messages.info(request, 'Your vote has been removed.')
    else:
        petition.votes.add(request.user)
        messages.success(request, 'Thank you for voting!')
    
    return redirect('movies.petitions')

def local_popularity_map(request):
    template_data = {}
    template_data['title'] = 'Local Popularity Map'
    return render(request, 'movies/local_popularity_map.html', {'template_data': template_data})

def trending_movies_api(request):
    """
    API endpoint that returns trending movies data by state.
    Calculates real data from purchase history.
    """
    # Get all US states
    us_states = [
        'Alabama', 'Alaska', 'Arizona', 'Arkansas', 'California', 'Colorado', 'Connecticut', 'Delaware',
        'Florida', 'Georgia', 'Hawaii', 'Idaho', 'Illinois', 'Indiana', 'Iowa', 'Kansas', 'Kentucky',
        'Louisiana', 'Maine', 'Maryland', 'Massachusetts', 'Michigan', 'Minnesota', 'Mississippi',
        'Missouri', 'Montana', 'Nebraska', 'Nevada', 'New Hampshire', 'New Jersey', 'New Mexico',
        'New York', 'North Carolina', 'North Dakota', 'Ohio', 'Oklahoma', 'Oregon', 'Pennsylvania',
        'Rhode Island', 'South Carolina', 'South Dakota', 'Tennessee', 'Texas', 'Utah', 'Vermont',
        'Virginia', 'Washington', 'West Virginia', 'Wisconsin', 'Wyoming'
    ]
    
    state_movie_data = {}
    
    # Calculate trending movies for each state
    for state in us_states:
        # Get all orders from this state
        state_orders = Order.objects.filter(state=state)
        
        if state_orders.exists():
            # Get movie purchase counts for this state
            movie_purchases = Item.objects.filter(
                order__state=state
            ).values('movie__name').annotate(
                total_quantity=Sum('quantity'),
                total_orders=Count('order', distinct=True)
            ).order_by('-total_quantity')
            
            if movie_purchases.exists():
                # Get the most popular movie
                most_popular = movie_purchases.first()
                movie_name = most_popular['movie__name']
                total_purchases = most_popular['total_quantity']
                
                # Calculate if it's trending (purchases in last 30 days vs total)
                thirty_days_ago = timezone.now() - timedelta(days=30)
                recent_purchases = Item.objects.filter(
                    order__state=state,
                    order__date__gte=thirty_days_ago,
                    movie__name=movie_name
                ).aggregate(recent_total=Sum('quantity'))['recent_total'] or 0
                
                # Consider trending if recent purchases are > 30% of total
                trending_threshold = total_purchases * 0.3
                is_trending = recent_purchases > trending_threshold
                
                state_movie_data[state] = {
                    'movie': movie_name,
                    'purchases': total_purchases,
                    'trending': is_trending
                }
            else:
                # No purchases in this state
                state_movie_data[state] = {
                    'movie': 'No purchases',
                    'purchases': 0,
                    'trending': False
                }
        else:
            # No orders from this state
            state_movie_data[state] = {
                'movie': 'No purchases',
                'purchases': 0,
                'trending': False
            }
    
    return JsonResponse({
        'success': True,
        'data': state_movie_data,
        'message': 'Trending movies data calculated from purchase history',
        'timestamp': str(timezone.now()),
        'api_version': '2.0',
        'total_states': len(state_movie_data),
        'calculation_method': 'Real-time purchase analysis'
    })
