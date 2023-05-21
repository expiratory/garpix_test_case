"""
Views for Photos
"""

from django.shortcuts import render, redirect
from .models import Photo


def gallery(request):
    """
    show for user all his photos
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        photos = Photo.objects.all()
        context = {}
        for photo in photos:
            if photo.user == request.user:
                context['photo'] = photo
        if not context:
            return redirect('home')
    return render(request, 'photos/gallery.html', context)



def view_photo(request, pk):
    """
    show for user photo defined by pk
    :param request:
    :param pk:
    :return:
    """
    if request.user.is_authenticated:
        photo = Photo.objects.get(id=pk)
        if photo.user == request.user:
            photo.count_of_views += 1
            photo.save()
            return render(request, 'photos/photo.html', {'photo': photo})
    return redirect('home')


def add_photo(request):
    """
    add photo for user
    :param request:
    :return:
    """
    if request.user.is_authenticated:
        if request.method == 'POST':
            user = request.user
            data = request.POST
            image = request.FILES.get('image')
            Photo.objects.create(
                title=data['title'],
                description=data['description'],
                image=image,
                user=user
            )
            return redirect('gallery')
    return redirect('home')


def change_photos_name(request, pk):
    """
    change name in defined by pk photo of user
    :param request:
    :param pk:
    :return:
    """
    if request.user.is_authenticated:
        photo = Photo.objects.get(id=pk)
        if photo.user == request.user:
            if request.method == 'POST':
                data = request.POST
                photo.title = data['title']
                photo.save()
                return redirect('gallery')
    return redirect('home')
