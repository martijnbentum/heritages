'''Image field that does not depend on Pillow.

ImageFileField replaces django's ImageField. Uploads are validated on
file extension and on the signature in the first bytes of the file.
'''
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.db import models

IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'jfif', 'png', 'gif', 'webp', 'tif', 'tiff',
    'bmp']

IMAGE_SIGNATURES = [
    b'\xff\xd8\xff',                 # jpeg
    b'\x89PNG\r\n\x1a\n',            # png
    b'GIF87a', b'GIF89a',            # gif
    b'II*\x00', b'MM\x00*',          # tiff
    b'BM',                           # bmp
]


def is_webp(header):
    return header[:4] == b'RIFF' and header[8:12] == b'WEBP'

validate_image_extension = FileExtensionValidator(IMAGE_EXTENSIONS)

def is_new_upload(f):
    '''files already in storage are committed; only new uploads are checked,
    so editing a record does not re-read (possibly missing) stored files.'''
    return not getattr(f, '_committed', False)

def validate_image(f):
    '''raises a ValidationError if a new upload does not have an image
    extension or does not start with the signature of a known image format.'''
    if not is_new_upload(f): return
    validate_image_extension(f)
    f.seek(0)
    header = f.read(12)
    f.seek(0)
    if is_webp(header): return
    if any(header.startswith(s) for s in IMAGE_SIGNATURES): return
    raise ValidationError('File is not a valid image.')


class ImageFileField(models.FileField):
    '''FileField for images that does not need Pillow.'''
    default_validators = [validate_image]

    def formfield(self, **kwargs):
        field = super().formfield(**kwargs)
        field.widget.attrs.setdefault('accept', 'image/*')
        return field
