import strawberry
import strawberry_django
from typing import List, Optional

from projects.models import Project
from projects.schema import ProjectType, UserType

from .models import Review
from notifications.tasks import send_system_notification, dispatch_notification


@strawberry_django.type(Review)
class ReviewType:
    id: strawberry.auto
    author: UserType
    target: UserType
    project: ProjectType
    rating: strawberry.auto
    comment: strawberry.auto
    created_at: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def reviews(self, info, user_id: int) -> List[ReviewType]:
        return Review.objects.filter(target_id=user_id)


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_review(
        self, info, project_id: int, rating: int, comment: Optional[str] = None
    ) -> ReviewType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        project = Project.objects.get(pk=project_id)
        if project.status != "completed":
            raise Exception("Project not completed")
        if Review.objects.filter(author=user, project=project).exists():
            raise Exception("Review already exists for this project")
        review = Review.objects.create(
            author=user,
            target=project.owner,
            project=project,
            rating=rating,
            comment=comment,
        )
        dispatch_notification(send_system_notification, review.target.id, 'New Review', f'{user.username} left you a review on {project.title}')
        return review
