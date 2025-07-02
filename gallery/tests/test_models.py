import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, override_settings
from gallery.models import Photo
from PIL import Image
import os

MEDIA_ROOT = tempfile.mkdtemp()


def generate_test_image(name="test.jpg", size=(100, 100), color=(255, 0, 0)):
    image = Image.new("RGB", size, color)
    temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
    image.save(temp_file, 'jpeg')
    temp_file.seek(0)
    return SimpleUploadedFile(name=name, content=temp_file.read(), content_type='image/jpeg')


@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PhotoModelTest(TestCase):

    def test_image_upload_and_variations_created(self):
        photo = Photo.objects.create(
            title='Test Photo', image=generate_test_image())

        # Variations are auto-generated (if PRE-RENDERED)
        self.assertTrue(photo.image)
        self.assertTrue(os.path.exists(photo.image.path))
        self.assertTrue(os.path.exists(photo.image.thumbnail.path))
        self.assertTrue(os.path.exists(photo.image.large.path))

    # def test_orphan_deletion_on_image_update(self):
    #     image1 = generate_test_image(name="original.jpg")
    #     photo = Photo.objects.create(title='Replace Image', image=image1)
    #     old_image_path = photo.image.path

    #     # Upload a new image with a different name
    #     image2 = generate_test_image(name="updated.jpg")
    #     photo.image = image2
    #     photo.save()

    #     self.assertEqual(os.path.exists(old_image_path),
    #                      os.path.exists(photo.image.path))
    #     self.assertFalse(os.path.exists(old_image_path)
    #                      )  # should now be deleted
    #     self.assertTrue(os.path.exists(photo.image.path))

@override_settings(MEDIA_ROOT=MEDIA_ROOT)
class PhotoVariationTest(TestCase):
    def test_image_variations_exist(self):
        photo = Photo.objects.create(title="Variation Test", image=generate_test_image())

        # Main image
        self.assertTrue(os.path.exists(photo.image.path))

        # Variation: thumbnail
        self.assertTrue(hasattr(photo.image, 'thumbnail'))
        self.assertTrue(os.path.exists(photo.image.thumbnail.path))

        # Variation: large
        self.assertTrue(hasattr(photo.image, 'large'))
        self.assertTrue(os.path.exists(photo.image.large.path))