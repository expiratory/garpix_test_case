from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('api/v1/photos/gallery/', views.gallery, name='gallery'),
    path('api/v1/photos/photo/<str:pk>/', views.viewPhoto, name='photo'),
    path('api/v1/photos/add/', views.addPhoto, name='add'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)