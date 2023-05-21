from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/v1/photos/gallery/', views.gallery, name='gallery'),
    path('api/v1/photos/photo/<str:pk>/', views.view_photo, name='photo'),
    path('api/v1/photos/add/', views.add_photo, name='add'),
    path('api/v1/photos/change_photos_name/<str:pk>/', views.change_photos_name, name='change_photos_name'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
