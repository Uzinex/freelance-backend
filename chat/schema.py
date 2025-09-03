import strawberry
import strawberry_django
from typing import List, Optional
from django.contrib.auth import get_user_model

from .models import Message, Room
from projects.models import Project
from projects.schema import ProjectType, UserType


@strawberry_django.type(Room)
class RoomType:
    id: strawberry.auto
    project: Optional[ProjectType]
    participants: List[UserType]
    created_at: strawberry.auto


@strawberry_django.type(Message)
class MessageType:
    id: strawberry.auto
    room: RoomType
    author: UserType
    content: strawberry.auto
    created_at: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def rooms(self, info) -> List[RoomType]:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        return Room.objects.filter(participants=user)

    @strawberry.field
    def messages(self, info, room_id: int) -> List[MessageType]:
        user = info.context.request.user
        room = Room.objects.get(pk=room_id)
        if not room.participants.filter(pk=user.pk).exists():
            raise Exception("Not permitted")
        return room.messages.order_by('created_at').all()


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_room(
        self,
        info,
        project_id: Optional[int],
        participants: List[int],
    ) -> RoomType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        participant_ids = set(participants)
        participant_ids.add(user.id)
        users = list(get_user_model().objects.filter(id__in=participant_ids))
        if len(users) != len(participant_ids):
            raise Exception("Invalid participants")
        project = None
        if project_id is not None:
            project = Project.objects.get(pk=project_id)
            allowed_ids = set([project.owner_id])
            allowed_ids.update(
                project.bids.values_list('freelancer_id', flat=True)
            )
            if not participant_ids.issubset(allowed_ids):
                raise Exception("Participants must be related to project")
        room = Room.objects.create(project=project)
        room.participants.set(users)
        return room

    @strawberry.mutation
    def send_message(
        self, info, room_id: int, content: str
    ) -> MessageType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        room = Room.objects.get(pk=room_id)
        if not room.participants.filter(pk=user.pk).exists():
            raise Exception("Not permitted")
        message = Message.objects.create(room=room, author=user, content=content)
        return message
