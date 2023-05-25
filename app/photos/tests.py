"""
    tests for photos app
"""
from datetime import datetime
from unittest import TestCase
import django
from django.conf import settings
from django.contrib.auth.models import User
import pytest
from rest_framework.test import APIClient
from .models import Photo
from .serializers import PhotoSerializer
from .views import PhotosViewSet

settings.configure()

django.setup()


class TestPhotosViewSet(TestCase):
    """
    Tests for PhotosViewSet class
    """

    def test_user_gallery_view(self, request):
        """
        Test that a user can view their gallery
        """
        user = User.objects.create(username='testuser', password='testPW123')
        Photo.objects.create(title="Test Photo 1", image="test1.jpg", user=user)
        Photo.objects.create(title="Test Photo 2", image="test2.jpg", user=user)

        request.user = user

        response = PhotosViewSet.as_view({'get': 'gallery'})(request.get('/photos/gallery/'))

        assert response.status_code == 200
        assert len(response.data['gallery']) == 2
        assert response.data['gallery'][0]['title'] == "Test Photo 1"
        assert response.data['gallery'][1]['title'] == "Test Photo 2"

    def test_view_specific_photo(self, request):
        """
        Test that a user can view a specific photo
        """
        user = User.objects.create(username='testuser', password='testPW123')
        photo = Photo.objects.create(title="Test Photo", image="test.jpg", user=user)

        request.user = user

        response = PhotosViewSet.as_view({'get': 'photo'})(request.get(f'/photos/{photo.pk}/'), pk=photo.pk)

        assert response.status_code == 200
        assert response.data['photo']['title'] == "Test Photo"
        assert response.data['photo']['count_of_views'] == 1

    def test_view_nonexistent_photo(self, request):
        """
        Test that a user cannot view a photo that doesn't exist
        """
        user = User.objects.create(username='testuser', password='testPW123')
        request.user = user

        response = PhotosViewSet.as_view({'get': 'photo'})(request.get('/photos/999/'), pk=999)

        assert response.status_code == 404
        assert response.data['message'] == "fail"
        assert response.data['description'] == "Photo matching query does not exist."

    def test_change_nonexistent_photo_title(self, request):
        """
        Test that a user cannot change the title of a photo that doesn't exist
        """
        user = User.objects.create(username='testuser', password='testPW123')
        request.user = user

        response = PhotosViewSet.as_view({'post': 'change_photo_title'})\
            (request.post('/photos/999/change_title/', data={'title': 'New Title'}), pk=999)

        assert response.status_code == 404
        assert response.data['message'] == "fail"
        assert response.data['description'] == "Photo matching query does not exist."

    def test_change_photo_title(self, request):
        """
        Test that a user can change the title of their photo
        """
        user = User.objects.create(username='testuser', password='testPW123')
        photo = Photo.objects.create(title="Test Photo", image="test.jpg", user=user)

        request.user = user

        response = PhotosViewSet.as_view({'post': 'change_photo_title'})\
            (request.post(f'/photos/{photo.pk}/change_title/', data={'title': 'New Title'}), pk=photo.pk)

        assert response.status_code == 200
        assert response.data['photo']['title'] == "New Title"

    def test_add_photo_to_gallery(self, request):
        """
        Test that a user can add a photo to their gallery
        """
        user = User.objects.create(username='testuser', password='testPW123')
        request.user = user

        response = PhotosViewSet.as_view({'post': 'add_photo'})\
            (request.post('/photos/add/', data={'title': 'New Photo', 'image': 'test.jpg'}))

        assert response.status_code == 200
        assert response.data['photo']['title'] == "New Photo"

    def test_add_photo_without_title_or_image(self):
        """
        Tests that a user cannot add a photo without providing a title or image.
        """
        client = APIClient()
        client.force_authenticate(user=User.objects.create_user(username='testuser',
                                                                password='testpass'))
        response = client.post('/photos/add_photo/', {'description': 'test description'})
        assert response.status_code == 400
        assert response.data['message'] == 'fail'
        assert 'title' in response.data['description']
        assert 'image' in response.data['description']

    def test_add_photo_with_invalid_image_file(self):
        """
        Tests that a user cannot add a photo with an invalid image file.
        """
        client = APIClient()
        client.force_authenticate(user=User.objects.create_user(username='testuser',
                                                                password='testpass'))
        response = client.post('/photos/add_photo/', {'title': 'test title',
                                                      'image': 'invalid_file'})
        assert response.status_code == 400
        assert response.data['message'] == 'fail'
        assert 'image' in response.data['description']

    def test_count_of_views_increases(self):
        """
        Tests that the count of views increases when a user views a photo.
        """
        user = User.objects.create_user(username='testuser', password='testpass')
        photo = Photo.objects.create(title='test title', image='test_image.jpg', user=user)
        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get(f'/photos/{photo.id}/photo/')
        assert response.status_code == 200
        assert response.data['photo']['count_of_views'] == 1

    def test_image_url_construction(self):
        """
        Tests that image URLs are properly constructed for each photo.
        """
        user = User.objects.create(username='testuser')
        Photo.objects.create(title='Test Photo 1', image='test1.jpg', user=user)
        Photo.objects.create(title='Test Photo 2', image='test2.jpg', user=user)

        client = APIClient()
        client.force_authenticate(user=user)
        response = client.get('/photos/gallery/')
        assert response.status_code == 200
        assert response.data['gallery'][0]['image'] == \
               'http://127.0.0.1:8000/static/media/test1.jpg'
        assert response.data['gallery'][1]['image'] == \
               'http://127.0.0.1:8000/static/media/test2.jpg'

    def test_authentication_and_authorization(self):
        """
        Tests authentication and authorization for each endpoint.
        """
        user1 = User.objects.create(username='testuser1')
        user2 = User.objects.create(username='testuser2')
        photo1 = Photo.objects.create(title='Test Photo 1', image='test1.jpg', user=user1)
        photo2 = Photo.objects.create(title='Test Photo 2', image='test2.jpg', user=user1)

        client = APIClient()
        response = client.get('/photos/gallery/')
        assert response.status_code == 401

        client.force_authenticate(user=user2)
        response = client.get('/photos/gallery/')
        assert response.status_code == 200
        assert len(response.data['gallery']) == 0

        client.force_authenticate(user=user1)
        response = client.get('/photos/gallery/')
        assert response.status_code == 200
        assert len(response.data['gallery']) == 2

        response = client.get(f'/photos/{photo1.id}/photo/')
        assert response.status_code == 200

        client.force_authenticate(user=user2)
        response = client.get(f'/photos/{photo1.id}/photo/')
        assert response.status_code == 403

        response = client.get(f'/photos/{photo2.id}/photo/')
        assert response.status_code == 200

        response = client.post(f'/photos/{photo1.id}/change_photo_title/', {'title': 'New Title'})
        assert response.status_code == 200
        assert response.data['photo']['title'] == 'New Title'

        client.force_authenticate(user=user2)
        response = client.post(f'/photos/{photo1.id}/change_photo_title/', {'title': 'New Title'})
        assert response.status_code == 403

    def test_error_handling(self):
        """
        Tests error handling for unexpected exceptions.
        """
        user = User.objects.create(username='testuser')
        client = APIClient()
        client.force_authenticate(user=user)

        response = client.post('/photos/add_photo/', {'description': 'Test Description'})
        assert response.status_code == 400
        assert response.data['message'] == 'fail'
        assert 'title' in response.data['description']

        with open('test.txt', 'w') as f:
            f.write('test')
        with open('test.txt', 'rb') as f:
            response = client.post('/photos/add_photo/',
                                   {'title': 'Test Title',
                                    'description': 'Test Description',
                                    'image': f})
            assert response.status_code == 400
            assert response.data['message'] == 'fail'
            assert 'The submitted file is empty.' in response.data['description']

        response = client.post('/photos/add_photo/',
                               {'title': 'Test Title',
                                'description': 'Test Description',
                                'image': 'not a file'})
        assert response.status_code == 400
        assert response.data['message'] == 'fail'
        assert 'the submitted data was not a file' in response.data['description']


class TestPhoto(TestCase):
    """
    Tests for Photo model
    """

    def test_create_photo_with_all_fields(self, mocker):
        """
        Tests that photo can be created with all fields
        """
        user = User.objects.create(username='testuser')
        mocker.patch('django.contrib.auth.models.User', return_value=user)
        photo = Photo.objects.create(title='Test Photo',
                                     description='Test Description',
                                     image='test.jpg', user=user)
        assert photo.title == 'Test Photo'
        assert photo.description == 'Test Description'
        assert photo.count_of_views == 0
        assert photo.image == 'test.jpg'
        assert photo.user == user

    def test_update_photo_title_and_description(self, mocker):
        """
        Test that title and description of photo can be changed
        """
        user = User.objects.create(username='testuser')
        mocker.patch('django.contrib.auth.models.User', return_value=user)
        photo = Photo.objects.create(title='Test Photo',
                                     description='Test Description',
                                     image='test.jpg',
                                     user=user)
        photo.title = 'Updated Title'
        photo.description = 'Updated Description'
        photo.save()
        updated_photo = Photo.objects.get(id=photo.id)
        assert updated_photo.title == 'Updated Title'
        assert updated_photo.description == 'Updated Description'

    def test_upload_image_exceeds_max_size(self, mocker):
        """
        Tests when upload image exceeds maximum size
        """
        user = User.objects.create(username='testuser')
        mocker.patch('django.contrib.auth.models.User', return_value=user)
        with pytest.raises(ValueError):
            Photo.objects.create(title='Test Photo',
                                 description='Test Description',
                                 image='large_image.jpg',
                                 user=user)

    def test_create_photo_blank_title_or_description(self, mocker):
        """
        Tests that photo could not be created without title
        """
        user = User.objects.create(username='testuser')
        mocker.patch('django.contrib.auth.models.User', return_value=user)
        with pytest.raises(ValueError):
            Photo.objects.create(title='', description='', image='test.jpg', user=user)

    def test_retrieve_photo_views_and_date(self, mocker):
        """
        Tests that count of views is 0 by default and date of creation is note None
        """
        user = User.objects.create(username='testuser')
        mocker.patch('django.contrib.auth.models.User', return_value=user)
        photo = Photo.objects.create(title='Test Photo',
                                     description='Test Description',
                                     image='test.jpg',
                                     user=user)
        assert photo.count_of_views == 0
        assert photo.date_of_creation is not None

    def test_create_photo_without_user(self):
        """
        Tests that photo can not be created without user
        """
        with pytest.raises(ValueError):
            Photo.objects.create(title='Test Photo',
                                 description='Test Description',
                                 image='test.jpg')


class TestPhotoSerializer(TestCase):
    """
    Tests for PhotoSerializer class
    """

    def test_serializer_serializes_photo(self):
        """
        Tests that the PhotoSerializer correctly serializes a Photo model.
        """
        user = User.objects.create(username='testuser')
        photo = Photo.objects.create(title='test title',
                                     description='test description',
                                     image='test.jpg',
                                     user=user)
        serializer = PhotoSerializer(photo)
        expected_data = {
            'title': 'test title',
            'description': 'test description',
            'count_of_views': 0,
            'date_of_creation': str(photo.date_of_creation),
            'image': photo.image.url,
            'user': {
                'id': user.id,
                'username': user.username
            }
        }
        assert serializer.data == expected_data

    def test_all_fields_present(self):
        """
        Tests that all fields of the Photo model are present in the serialized output.
        """
        user = User.objects.create(username='testuser')
        photo = Photo.objects.create(title='test title',
                                     description='test description',
                                     image='test.jpg',
                                     user=user)
        serializer = PhotoSerializer(photo)
        assert set(serializer.data.keys()) == {'title',
                                               'description',
                                               'count_of_views',
                                               'date_of_creation',
                                               'image',
                                               'user'}

    def test_missing_fields(self):
        """
        Tests edge cases where the image, title,
        or description fields are missing from the Photo model.
        """
        user = User.objects.create(username='testuser')
        photo = Photo.objects.create(image='test.jpg', user=user)
        serializer = PhotoSerializer(photo)
        expected_data = {
            'title': '',
            'description': '',
            'count_of_views': 0,
            'date_of_creation': str(photo.date_of_creation),
            'image': photo.image.url,
            'user': {
                'id': user.id,
                'username': user.username
            }
        }
        assert serializer.data == expected_data

    def test_negative_count_of_views(self):
        """
        Tests edge case where the count_of_views field is negative.
        """
        user = User.objects.create(username='testuser')
        photo = Photo.objects.create(title='test title',
                                     description='test description',
                                     image='test.jpg',
                                     user=user,
                                     count_of_views=-1)
        serializer = PhotoSerializer(photo)
        expected_data = {
            'title': 'test title',
            'description': 'test description',
            'count_of_views': 0,
            'date_of_creation': str(photo.date_of_creation),
            'image': photo.image.url,
            'user': {
                'id': user.id,
                'username': user.username
            }
        }
        assert serializer.data == expected_data

    def test_user_field_serialized_correctly(self):
        """
        Tests that the user field is correctly serialized as a nested object.
        """
        user = User.objects.create(username='testuser')
        photo = Photo.objects.create(title='test title',
                                     description='test description',
                                     image='test.jpg',
                                     user=user)
        serializer = PhotoSerializer(photo)
        expected_data = {
            'title': 'test title',
            'description': 'test description',
            'count_of_views': 0,
            'date_of_creation': str(photo.date_of_creation),
            'image': photo.image.url,
            'user': {
                'id': user.id,
                'username': user.username
            }
        }
        assert serializer.data == expected_data

    def test_future_date_of_creation(self):
        """
        Tests edge case where the date_of_creation field is in the future.
        """
        user = User.objects.create(username='testuser')
        future_date = datetime.date.today() + datetime.timedelta(days=1)
        photo = Photo.objects.create(title='test title',
                                     description='test description',
                                     image='test.jpg',
                                     user=user,
                                     date_of_creation=future_date)
        serializer = PhotoSerializer(photo)
        expected_data = {
            'title': 'test title',
            'description': 'test description',
            'count_of_views': 0,
            'date_of_creation': str(photo.date_of_creation),
            'image': photo.image.url,
            'user': {
                'id': user.id,
                'username': user.username
            }
        }
        assert serializer.data == expected_data
