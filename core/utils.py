import datetime
import os
import uuid
from typing import Optional


def get_file_extension(file_obj, lowercase=True) -> Optional[str]:
    name = getattr(file_obj, 'name', None)

    if not name or not isinstance(name, str):
        return None

    try:
        _, ext = os.path.splitext(name)
    except (TypeError, ValueError):
        return None

    if not ext:
        return None

    ext = ext.lstrip('.')
    return ext.lower() if lowercase else ext

def generate_upload_path(base_folder, filename):
    try:
        ext = os.path.splitext(filename)[1].lower()
        if not ext:
            ext = ''
    except Exception:
        ext = ''

    timestamp = datetime.datetime.now().strftime('%Y/%m')
    unique_name = uuid.uuid4().hex
    return f'{base_folder}/{timestamp}/{unique_name}{ext}'

def category_image_upload_to(instance, filename):
    return generate_upload_path('categories', filename)

def ad_image_upload_to(instance, filename):
    return generate_upload_path('ad', filename)
