import strawberry
import strawberry_django
from typing import List

from .models import Notification


@strawberry_django.type(Notification)
class NotificationType:
    id: strawberry.auto
    type: strawberry.auto
    title: strawberry.auto
    message: strawberry.auto
    is_read: strawberry.auto
    created_at: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def notifications(self, info) -> List[NotificationType]:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        return list(Notification.objects.filter(user=user).order_by("-created_at"))


@strawberry.type
class Mutation:
    @strawberry.mutation(name="markNotificationRead")
    def mark_notification_read(self, info, id: int) -> NotificationType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        try:
            notification = Notification.objects.get(pk=id, user=user)
        except Notification.DoesNotExist:
            raise Exception("Not found")
        notification.is_read = True
        notification.save()
        return notification
