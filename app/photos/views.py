"""
ViewSet for photos
"""
from django.conf import settings
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from .serializers import PhotoSerializer
from .models import Photo


class PhotosViewSet(GenericViewSet):
    """
    ViewSet for Photos
    """
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer

    @action(methods=['get'], detail=False)
    def gallery(self, request):
        """
        user's gallery
        :param request: method GET
        :return Response: json that includes queryset of user's photos
        """
        gallery = Photo.objects.filter(user=request.user).values()
        for photo in gallery:
            photo['image'] = request.get_host() + settings.STATIC_URL + settings.MEDIA_URL[1:] + photo['image']
        return Response({'gallery': gallery})

    @action(methods=['get'], detail=True)
    def photo(self, request, pk):
        """
        show user his photo defined by pk
        :param request: method GET
        :param pk: primary key - photo.id
        :return Response: if success defined photo json representation
                          else {'message': 'fail', 'description': 'permission denied'}
        """
        try:
            photo = Photo.objects.get(pk=pk)
            if photo.user != request.user:
                return Response({'message': 'fail', 'description': 'permission denied'})
            photo.count_of_views += 1
            photo.save()
            photo['image'] = request.get_host() + settings.STATIC_URL + settings.MEDIA_URL[1:] + photo['image']
            return Response({'photo': PhotoSerializer(photo).data})
        except Photo.DoesNotExist as e:
            return Response({'message': 'fail', 'description': str(e)})

    @action(methods=['post'], detail=True)
    def change_photo_title(self, request, pk):
        """
        allows user to change title of his photo defined by pk
        :param request: method POST: dict = {'title': 'value'}
        :param pk: primary key - photo.id
        :return Response: if success defined photo json representation with new title
                          else {'message': 'fail', 'description': 'permission denied'}
        """
        try:
            photo = Photo.objects.get(pk=pk)
            if photo.user != request.user:
                return Response({'message': 'fail', 'description': 'permission denied'})
            data = request.POST
            photo.title = data['title']
            photo.save()
            photo['image'] = request.get_host() + settings.STATIC_URL + settings.MEDIA_URL[1:] + photo['image']
            return Response({'photo': PhotoSerializer(photo).data})
        except Photo.DoesNotExist as e:
            return Response({'message': 'fail', 'description': str(e)})
        except KeyError as e:
            return Response({'message': 'fail', 'description': str(e)})

    @action(methods=['post'], detail=False)
    def add_photo(self, request):
        """
        allows user to add photo
        :param request: method POST: image file, dict = {'title': 'value'
                                                         'description': 'value'}
        :return Response: added photo json representation
        """
        try:
            data = request.POST
            image = request.FILES.get('image')
            user = request.user
            photo = Photo.objects.create(
                title=data['title'],
                description=data['description'],
                image=image,
                user=user)
            photo['image'] = request.get_host() + settings.STATIC_URL + settings.MEDIA_URL[1:] + photo['image']
            return Response({'photo': PhotoSerializer(photo).data})
        except KeyError as e:
            return Response({'message': 'fail', 'description': str(e)})
        except ValueError as e:
            return Response({'message': 'fail', 'description': str(e)})
        except TypeError as e:
            return Response({'message': 'fail', 'description': str(e)})
        except Exception as e:
            return Response({'message': 'fail', 'description': str(e)})
