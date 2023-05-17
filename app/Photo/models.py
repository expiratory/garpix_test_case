from django.db import models


class Photo(models.Model):
    title = models.CharField(max_length=256)
    count_of_views = models.PositiveIntegerField(default=0, editable=False)
    date_of_creation = models.DateField(auto_now_add=True)

    def __str__(self):
        return self.title
