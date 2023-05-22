"""
ViewSet for photos
"""

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
        if success it makes json with qs of user's photos
        :param request:
        :return Response:
        """
        gallery = Photo.objects.filter(user=request.user).values()
        if not gallery:
            return Response({'message': 'error', 'description': 'photos not found'})
        return Response({'gallery': gallery})

    @action(methods=['get'], detail=True)
    def photo(self, request, pk):
        """
        if success it makes json with photo defined by pk
        :param request:
        :param pk:
        :return Response:
        """
        photo = Photo.objects.get(pk=pk)
        if photo.user != request.user:
            return Response({'message': 'error', 'description': 'access denied'})
        photo.count_of_views += 1
        photo.save()
        return Response({'photo': PhotoSerializer(photo).data})

    @action(methods=['post'], detail=True)
    def change_photo_title(self, request, pk):
        """
        allows user to change title of the photo defined by pk
        and response with json with result in case of success
        :param request:
        :param pk:
        :return Response:
        """
        photo = Photo.objects.get(pk=pk)
        if photo.user != request.user:
            return Response({'message': 'error', 'description': 'permission denied'})
        data = request.POST
        photo.title = data['title']
        photo.save()
        return Response({'photo': PhotoSerializer(photo).data})

    @action(methods=['post'], detail=False)
    def add_photo(self, request):
        """
        allows user to add photo and response
        with json with result in case of success
        :param request:
        :return Response:
        """
        data = request.POST
        image = request.FILES.get('image')
        user = request.user
        photo = Photo.objects.create(
            title=data['title'],
            description=data['description'],
            image=image,
            user=user)
        if not photo:
            return Response({'message': 'fail', 'description': 'photo was not added'})
        return Response({'message': 'success', 'description': 'photo was added'})
