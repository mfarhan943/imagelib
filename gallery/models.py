from django.db import models
from stdimage.models import StdImageField

class Photo(models.Model):
    title = models.CharField(max_length=100)
    image = StdImageField(
        upload_to='photos/',
        variations={
            'thumbnail': (150, 150, True),
            'large': (800, 600),
        },
        delete_orphans=True,
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
