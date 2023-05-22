"""
serializers for photos
"""

from rest_framework import serializers
from .models import Photo


class PhotoSerializer(serializers.ModelSerializer):
    """
    Photo model serializer
    """

    class Meta:
        """
        Meta class
        """
        model = Photo
        fields = ('title', 'description', 'count_of_views', 'date_of_creation', 'image', 'user')
