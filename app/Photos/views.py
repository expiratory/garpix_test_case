from django.shortcuts import render, redirect

# Create your views here.
from .models import Photo


def gallery(request):
    photos = Photo.objects.all()
    context = {
        'photos': photos,
    }
    return render(request, 'photos/gallery.html', context)


def view_photo(request, pk):
    photo = Photo.objects.get(id=pk)
    photo.count_of_views += 1
    photo.save()
    return render(request, 'photos/photo.html', {'photo': photo})


def add_photo(request):

    if request.method == 'POST':
        data = request.POST
        image = request.FILES.get('image')
        photo = Photo.objects.create(
            title=data['title'],
            description=data['description'],
            image=image
        )
        return redirect('gallery')
    return render(request, 'photos/add.html')


def change_photos_name(request, pk):
    photo = Photo.objects.get(id=pk)
    if request.method == 'POST':
        data = request.POST
        photo.title = data['title']
        photo.save()
        return redirect('gallery')
    return render(request, 'photos/change_photos_name.html')
