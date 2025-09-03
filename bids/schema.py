import strawberry
import strawberry_django
from decimal import Decimal
from typing import List

from projects.models import Project
from projects.schema import ProjectType, UserType
from .models import Bid
from notifications.tasks import send_system_notification, dispatch_notification


@strawberry_django.type(Bid)
class BidType:
    id: strawberry.auto
    project: ProjectType
    freelancer: UserType
    amount: strawberry.auto
    message: strawberry.auto
    status: strawberry.auto
    created_at: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def bids(self, info, project_id: int) -> List[BidType]:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        project = Project.objects.get(pk=project_id)
        if project.owner == user:
            return list(project.bids.all())
        return list(Bid.objects.filter(project=project, freelancer=user))


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_bid(self, info, project_id: int, amount: Decimal, message: str) -> BidType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        project = Project.objects.get(pk=project_id)
        if project.owner == user:
            raise Exception("Project owners cannot bid on their own projects")
        bid = Bid.objects.create(
            project=project, freelancer=user, amount=amount, message=message
        )
        dispatch_notification(send_system_notification, project.owner.id, 'New Bid', f'You have a new bid on {project.title}')
        return bid

    @strawberry.mutation
    def accept_bid(self, info, id: int) -> BidType:
        user = info.context.request.user
        bid = Bid.objects.get(pk=id)
        if bid.project.owner != user:
            raise Exception("Not permitted")
        bid.status = "accepted"
        bid.save()
        dispatch_notification(send_system_notification, bid.freelancer.id, 'Bid Accepted', f'Your bid on {bid.project.title} was accepted')
        return bid

    @strawberry.mutation
    def reject_bid(self, info, id: int) -> BidType:
        user = info.context.request.user
        bid = Bid.objects.get(pk=id)
        if bid.project.owner != user:
            raise Exception("Not permitted")
        bid.status = "rejected"
        bid.save()
        dispatch_notification(send_system_notification, bid.freelancer.id, 'Bid Rejected', f'Your bid on {bid.project.title} was rejected')
        return bid
