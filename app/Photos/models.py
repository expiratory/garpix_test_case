from django.contrib.auth.models import User
from django.db import models


class Photo(models.Model):
    title = models.CharField(max_length=256, null=False, blank=False)
    description = models.CharField(max_length=512, default='')
    count_of_views = models.PositiveIntegerField(default=0, editable=False)
    date_of_creation = models.DateField(auto_now_add=True, editable=False)
    image = models.ImageField(null=False, blank=False)
    user = models.ForeignKey(User, verbose_name='Пользователь', on_delete=models.CASCADE)

    def __str__(self):
        return self.title
