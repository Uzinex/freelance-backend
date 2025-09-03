import strawberry
import strawberry_django
from typing import List

from django.contrib.auth import get_user_model

from accounts.models import CustomUser
from projects.models import Project
from bids.models import Bid
from reviews.models import Review
from payments.models import Transaction


def _require_admin(info):
    user = info.context.request.user
    if not user.is_authenticated or getattr(user, "role", None) != "admin":
        raise Exception("Not authorized")


@strawberry_django.type(get_user_model())
class UserType:
    id: strawberry.auto
    username: strawberry.auto
    email: strawberry.auto
    role: strawberry.auto
    is_active: strawberry.auto


@strawberry_django.type(Project)
class ProjectType:
    id: strawberry.auto
    title: strawberry.auto
    owner: UserType
    status: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(Bid)
class BidType:
    id: strawberry.auto
    project: ProjectType
    freelancer: UserType
    amount: strawberry.auto
    status: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(Review)
class ReviewType:
    id: strawberry.auto
    author: UserType
    target: UserType
    project: ProjectType
    rating: strawberry.auto
    created_at: strawberry.auto


@strawberry_django.type(Transaction)
class TransactionType:
    id: strawberry.auto
    wallet: strawberry.auto
    amount: strawberry.auto
    type: strawberry.auto
    status: strawberry.auto
    created_at: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def all_users(self, info) -> List[UserType]:
        _require_admin(info)
        return CustomUser.objects.all()

    @strawberry.field
    def all_projects(self, info) -> List[ProjectType]:
        _require_admin(info)
        return Project.objects.all()

    @strawberry.field
    def all_bids(self, info) -> List[BidType]:
        _require_admin(info)
        return Bid.objects.all()

    @strawberry.field
    def all_reviews(self, info) -> List[ReviewType]:
        _require_admin(info)
        return Review.objects.all()

    @strawberry.field
    def all_transactions(self, info) -> List[TransactionType]:
        _require_admin(info)
        return Transaction.objects.all()


@strawberry.type
class Mutation:
    @strawberry.mutation
    def ban_user(self, info, user_id: int) -> bool:
        _require_admin(info)
        user = CustomUser.objects.get(pk=user_id)
        user.is_active = False
        user.save()
        return True

    @strawberry.mutation
    def delete_review(self, info, review_id: int) -> bool:
        _require_admin(info)
        Review.objects.filter(pk=review_id).delete()
        return True

    @strawberry.mutation
    def resolve_dispute(self, info, bid_id: int) -> bool:
        _require_admin(info)
        bid = Bid.objects.get(pk=bid_id)
        bid.status = "resolved"
        bid.save()
        return True
