from celery import shared_task
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from .models import Notification


def dispatch_notification(task, *args, **kwargs):
    try:
        task.delay(*args, **kwargs)
    except Exception:
        task.apply(args=args, kwargs=kwargs)


@shared_task
def send_email_notification(user_id, title, message):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    if user.email:
        send_mail(title, message, None, [user.email], fail_silently=True)
    Notification.objects.create(user=user, type="email", title=title, message=message)


@shared_task
def send_sms_notification(user_id, message):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    Notification.objects.create(
        user=user, type="sms", title="SMS Notification", message=message
    )


@shared_task
def send_system_notification(user_id, title, message):
    User = get_user_model()
    user = User.objects.get(pk=user_id)
    Notification.objects.create(user=user, type="system", title=title, message=message)
