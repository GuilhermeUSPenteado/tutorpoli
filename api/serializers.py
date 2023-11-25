from rest_framework import serializers

from forum.models import Movie

class MovieSerializer(serializers.ModelSerializer):
    # review_set = serializers.PrimaryKeyRelatedField(many=True, queryset=Review.objects.all()) 
    class Meta:
        model = Movie
        fields = ['id', 'name', 'release_year', 'poster_url']
