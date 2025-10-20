
from django.db import models
from django.contrib.auth.models import User
from django.db.models import Avg

class Movie(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    price = models.IntegerField()
    description = models.TextField()
    image = models.ImageField(upload_to='movie_images/')
    average_rating = models.FloatField(default=0.0, null=True, blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.name

class Review(models.Model):
    id = models.AutoField(primary_key=True)
    comment = models.CharField(max_length=255)
    date = models.DateTimeField(auto_now_add=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    reported = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie.name

class Petition(models.Model):
    id = models.AutoField(primary_key=True)
    movie_title = models.CharField(max_length=255)
    description = models.TextField()
    created_date = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    votes = models.ManyToManyField(User, related_name='petition_votes', blank=True)

    def __str__(self):
        return str(self.id) + ' - ' + self.movie_title

    def get_vote_count(self):
        return self.votes.count()

    def has_user_voted(self, user):
        return self.votes.filter(id=user.id).exists()

class Rating(models.Model):
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stars = models.IntegerField(choices=[(i, i) for i in range(1, 6)]) # 1 to 5 stars

    class Meta:
        # Ensures a user can only rate a specific movie once
        unique_together = ('movie', 'user')

    def save(self, *args, **kwargs):
        # Call the original save method first
        super().save(*args, **kwargs)
        
        # After saving a rating, recalculate and update the movie's average rating
        # We access the related movie through the 'movie' foreign key
        movie_ratings = self.movie.ratings.all()
        self.movie.average_rating = movie_ratings.aggregate(Avg('stars'))['stars__avg']
        self.movie.save()