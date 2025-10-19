
from django.shortcuts import render, redirect, get_object_or_404
from .models import Movie, Review, Petition
from django.contrib.auth.decorators import login_required
from django.contrib import messages

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
    # Hard-coded placeholder data for movie popularity by state
    state_movie_data = {
        'California': {'movie': 'Inception', 'purchases': 1250, 'trending': True},
        'Texas': {'movie': 'Saving Private Ryan', 'purchases': 980, 'trending': True},
        'Florida': {'movie': 'The Conjuring', 'purchases': 750, 'trending': False},
        'New York': {'movie': 'Inception', 'purchases': 1100, 'trending': True},
        'Pennsylvania': {'movie': 'Saving Private Ryan', 'purchases': 650, 'trending': False},
        'Illinois': {'movie': 'The Conjuring', 'purchases': 580, 'trending': True},
        'Ohio': {'movie': 'Inception', 'purchases': 520, 'trending': False},
        'Georgia': {'movie': 'Saving Private Ryan', 'purchases': 480, 'trending': True},
        'North Carolina': {'movie': 'The Conjuring', 'purchases': 420, 'trending': False},
        'Michigan': {'movie': 'Inception', 'purchases': 380, 'trending': True},
        'New Jersey': {'movie': 'Saving Private Ryan', 'purchases': 350, 'trending': False},
        'Virginia': {'movie': 'The Conjuring', 'purchases': 320, 'trending': True},
        'Washington': {'movie': 'Inception', 'purchases': 290, 'trending': False},
        'Arizona': {'movie': 'Saving Private Ryan', 'purchases': 270, 'trending': True},
        'Massachusetts': {'movie': 'The Conjuring', 'purchases': 250, 'trending': False},
        'Tennessee': {'movie': 'Inception', 'purchases': 230, 'trending': True},
        'Indiana': {'movie': 'Saving Private Ryan', 'purchases': 210, 'trending': False},
        'Missouri': {'movie': 'The Conjuring', 'purchases': 190, 'trending': True},
        'Maryland': {'movie': 'Inception', 'purchases': 180, 'trending': False},
        'Wisconsin': {'movie': 'Saving Private Ryan', 'purchases': 170, 'trending': True},
        'Colorado': {'movie': 'The Conjuring', 'purchases': 160, 'trending': False},
        'Minnesota': {'movie': 'Inception', 'purchases': 150, 'trending': True},
        'South Carolina': {'movie': 'Saving Private Ryan', 'purchases': 140, 'trending': False},
        'Alabama': {'movie': 'The Conjuring', 'purchases': 130, 'trending': True},
        'Louisiana': {'movie': 'Inception', 'purchases': 120, 'trending': False},
        'Kentucky': {'movie': 'Saving Private Ryan', 'purchases': 110, 'trending': True},
        'Oregon': {'movie': 'The Conjuring', 'purchases': 100, 'trending': False},
        'Oklahoma': {'movie': 'Inception', 'purchases': 95, 'trending': True},
        'Connecticut': {'movie': 'Saving Private Ryan', 'purchases': 90, 'trending': False},
        'Utah': {'movie': 'The Conjuring', 'purchases': 85, 'trending': True},
        'Iowa': {'movie': 'Inception', 'purchases': 80, 'trending': False},
        'Nevada': {'movie': 'Saving Private Ryan', 'purchases': 75, 'trending': True},
        'Arkansas': {'movie': 'The Conjuring', 'purchases': 70, 'trending': False},
        'Mississippi': {'movie': 'Inception', 'purchases': 65, 'trending': True},
        'Kansas': {'movie': 'Saving Private Ryan', 'purchases': 60, 'trending': False},
        'New Mexico': {'movie': 'The Conjuring', 'purchases': 55, 'trending': True},
        'Nebraska': {'movie': 'Inception', 'purchases': 50, 'trending': False},
        'West Virginia': {'movie': 'Saving Private Ryan', 'purchases': 45, 'trending': True},
        'Idaho': {'movie': 'The Conjuring', 'purchases': 40, 'trending': False},
        'Hawaii': {'movie': 'Inception', 'purchases': 35, 'trending': True},
        'New Hampshire': {'movie': 'Saving Private Ryan', 'purchases': 30, 'trending': False},
        'Maine': {'movie': 'The Conjuring', 'purchases': 25, 'trending': True},
        'Montana': {'movie': 'Inception', 'purchases': 20, 'trending': False},
        'Rhode Island': {'movie': 'Saving Private Ryan', 'purchases': 18, 'trending': True},
        'Delaware': {'movie': 'The Conjuring', 'purchases': 15, 'trending': False},
        'South Dakota': {'movie': 'Inception', 'purchases': 12, 'trending': True},
        'North Dakota': {'movie': 'Saving Private Ryan', 'purchases': 10, 'trending': False},
        'Alaska': {'movie': 'The Conjuring', 'purchases': 8, 'trending': True},
        'Vermont': {'movie': 'Inception', 'purchases': 6, 'trending': False},
        'Wyoming': {'movie': 'Saving Private Ryan', 'purchases': 4, 'trending': True}
    }
    
    template_data = {}
    template_data['title'] = 'Local Popularity Map'
    template_data['state_movie_data'] = state_movie_data
    return render(request, 'movies/local_popularity_map.html', {'template_data': template_data})
