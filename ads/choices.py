from django.db import models


class DataType(models.TextChoices):
    TEXT = 'text', 'Text'
    NUMBER = 'number', 'Number'
    BOOLEAN = 'bool', 'Boolean'
    CHOICE = 'choice', 'Choice'
