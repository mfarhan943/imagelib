import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from gallery.models import Photo
from PIL import Image
import os
from pictures.tasks import _process_picture

MEDIA_ROOT = tempfile.mkdtemp()


def generate_test_image(name="test.jpg", size=(100, 100), color=(255, 0, 0)):
    image = Image.new("RGB", size, color)
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(temp_file, 'jpeg')
    temp_file.seek(0)
    return SimpleUploadedFile(name=name, content=temp_file.read(), content_type='image/jpeg')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PhotoModelTest(TestCase):
    def test_image_file_saved(self):
        photo = Photo.objects.create(
            title='Test Photo', image=generate_test_image("test1.jpg"))

        self.assertTrue(photo.image)
        self.assertTrue(os.path.exists(photo.image.path))

@override_settings(
    MEDIA_ROOT=MEDIA_ROOT,
    PICTURES={
        "USE_PLACEHOLDERS": False,
        "PIXEL_DENSITIES": [1, 2],
        "PROCESSOR": "pictures.tasks._process_picture",
    },
    
)
class PhotoPictureFieldTest(TestCase):
    def test_picture_variations_exist_on_disk(self):
        photo = Photo.objects.create(
            title='Responsive Test',
            image=generate_test_image("responsive.jpg", size=(800, 600))
        )

        field = photo.image
        storage_tuple = field.storage.deconstruct()  # ✅ use this instead
        file_name = field.name
        _process_picture(storage_tuple, file_name)


        parent_dir = os.path.splitext(file_name)[0]
        ratio = "3_2"
        print("Image variations stored at:", os.path.join(MEDIA_ROOT, parent_dir, ratio))
        print("Files:", os.listdir(os.path.join(MEDIA_ROOT, parent_dir, ratio)))

        sizes = [100, 200, 300, 400, 500, 600, 700, 800]

        for width in sizes:
            path = os.path.join(
                MEDIA_ROOT, parent_dir, ratio, f"{width}w.WEBP"
            )
            self.assertTrue(os.path.exists(path), f"Missing: {path}")
