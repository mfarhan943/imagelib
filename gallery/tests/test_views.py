import io
import os
import tempfile
from django.test import TestCase, override_settings
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from PIL import Image
from gallery.models import Photo
from pictures.tasks import _process_picture

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

@override_settings(
    MEDIA_ROOT=MEDIA_ROOT,
    PICTURES={
        "USE_PLACEHOLDERS": False,
        "PIXEL_DENSITIES": [1, 2],
        "BREAKPOINTS": {"mobile": 576, "desktop": 1200},
        "CONTAINER_WIDTH": 1200,
        "GRID_COLUMNS": 12,
        "FILE_TYPES": ["WEBP"],
        "PROCESSOR": "pictures.tasks._process_picture",
    },
)
class PhotoUploadViewTest(TestCase):
    def test_upload_photo_successfully(self):
        upload_url = reverse('upload_photo')
        image_file = generate_test_image_file(size=(800, 600))  # ensure large enough for size variations.

        response = self.client.post(upload_url, {
            'title': 'Form Upload Test',
            'image': image_file,
        }, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'gallery/list.html')
        self.assertContains(response, 'Form Upload Test')

        self.assertEqual(Photo.objects.count(), 1)
        photo = Photo.objects.first()
        field = photo.image
        self.assertTrue(os.path.exists(field.path))  # main image

        storage_tuple = field.storage.deconstruct()
        file_name = field.name
        _process_picture(storage_tuple, file_name)

        parent_dir = os.path.splitext(file_name)[0]
        ratio = "3_2"
        for width in [100, 200, 400, 800]:
            variation_path = os.path.join(MEDIA_ROOT, parent_dir, ratio, f"{width}w.WEBP")
            self.assertTrue(os.path.exists(variation_path), f"Missing: {variation_path}")
