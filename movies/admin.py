from django.contrib import admin
from .models import Movie, Review, Petition

class MovieAdmin(admin.ModelAdmin):
    ordering = ['name']
    search_fields = ['name']

class PetitionAdmin(admin.ModelAdmin):
    list_display = ['movie_title', 'created_by', 'created_date', 'get_vote_count']
    ordering = ['-created_date']
    search_fields = ['movie_title', 'created_by__username']

admin.site.register(Movie, MovieAdmin)
admin.site.register(Review)
admin.site.register(Petition, PetitionAdmin)