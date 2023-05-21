from django.shortcuts import render, redirect

# Create your views here.
from rest_framework import serializers

from .models import Photo


def gallery(request):
    photos = Photo.objects.all()
    context = {}
    for photo in photos:
        if photo.user == request.user:
            context['photo'] = photo
    if 'photo' in context:
        return render(request, 'photos/gallery.html', context)
    return redirect('home')


def view_photo(request, pk):
    photo = Photo.objects.get(id=pk)
    if photo.user == request.user:
        photo.count_of_views += 1
        photo.save()
        return render(request, 'photos/photo.html', {'photo': photo})
    return redirect('home')


def add_photo(request):
    if request.method == 'POST':
        data = request.POST
        image = request.FILES.get('image')
        photo = Photo.objects.create(
            title=data['title'],
            description=data['description'],
            image=image,
            user=request.user
        )
        return redirect('gallery')
    return redirect('home')


def change_photos_name(request, pk):
    photo = Photo.objects.get(id=pk)
    if photo.user == request.user:
        if request.method == 'POST':
            data = request.POST
            photo.title = data['title']
            photo.save()
            return redirect('gallery')
    return redirect('home')
