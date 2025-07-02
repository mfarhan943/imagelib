import io
import os
import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from gallery.models import Photo

MEDIA_ROOT = tempfile.mkdtemp()

def generate_test_image_file(name="test.jpg", size=(100, 100), color=(255, 0, 0)):
    file_obj = io.BytesIO()
    image = Image.new("RGB", size, color)
    image.save(file_obj, 'JPEG')
    file_obj.seek(0)
    return SimpleUploadedFile(name, file_obj.read(), content_type='image/jpeg')

class PhotoListViewTest(TestCase):
    def setUp(self):
        self.photo = Photo.objects.create(
            title="Test View",
            image=generate_test_image_file()
        )

    def test_list_view(self):
        response = self.client.get(reverse('photo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.photo.title)

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PhotoUploadViewTest(TestCase):
    def test_upload_photo_successfully(self):
        upload_url = reverse('upload_photo')
        image_file = generate_test_image_file()

        response = self.client.post(upload_url, {
            'title': 'Form Upload Test',
            'image': image_file,
        }, follow=True)

        # It redirects to the photo list
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gallery/list.html')
        self.assertContains(response, 'Form Upload Test')

        # Photo saved
        self.assertEqual(Photo.objects.count(), 1)
        photo = Photo.objects.first()

        # Main image and variations exist
        self.assertTrue(os.path.exists(photo.image.path))
        self.assertTrue(os.path.exists(photo.image.thumbnail.path))
        self.assertTrue(os.path.exists(photo.image.large.path))