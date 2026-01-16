from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _


validate_phone = RegexValidator(
    regex=r'^\+?[1-9]\d{7,14}$',
    message=_('Enter a valid international phone number.'),
    code='invalid_phone',
)
