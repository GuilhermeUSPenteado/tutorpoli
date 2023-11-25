from django.shortcuts import render

# Create your views here.
from rest_framework import generics

from forum.models import Movie
from .serializers import MovieSerializer

class MovieList(generics.ListCreateAPIView):               
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
