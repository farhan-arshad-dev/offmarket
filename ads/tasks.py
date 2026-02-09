from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail


@shared_task
def send_ad_confimation_email(ad_id, user_email):
    subject = 'Ad Confirmation'
    message = f'Your Ad with ID {ad_id} has been received and is being processed.'
    return send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user_email])
