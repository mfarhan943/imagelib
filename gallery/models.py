from django.db import models
from pictures.models import PictureField

class Photo(models.Model):
    title = models.CharField(max_length=100)
    image = PictureField(
        upload_to='photos',
        aspect_ratios=['3/2'],  # defines variation key used in template
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
