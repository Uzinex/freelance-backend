import strawberry
import strawberry_django
from decimal import Decimal
from typing import List, Optional
from django.contrib.auth import get_user_model
from .models import Project


@strawberry_django.type(get_user_model())
class UserType:
    id: strawberry.auto
    username: strawberry.auto
    email: strawberry.auto


@strawberry_django.type(Project)
class ProjectType:
    id: strawberry.auto
    owner: 'UserType'
    title: strawberry.auto
    description: strawberry.auto
    budget_min: strawberry.auto
    budget_max: strawberry.auto
    status: strawberry.auto
    created_at: strawberry.auto
    updated_at: strawberry.auto


@strawberry.type
class Query:
    @strawberry.field
    def projects(self, info) -> List[ProjectType]:
        return Project.objects.all()

    @strawberry.field
    def project(self, info, id: int) -> Optional[ProjectType]:
        return Project.objects.filter(pk=id).first()


@strawberry.type
class Mutation:
    @strawberry.mutation
    def create_project(
        self,
        info,
        title: str,
        description: str,
        budget_min: Optional[Decimal] = None,
        budget_max: Optional[Decimal] = None,
    ) -> ProjectType:
        user = info.context.request.user
        if not user.is_authenticated:
            raise Exception("Authentication required")
        project = Project.objects.create(
            owner=user,
            title=title,
            description=description,
            budget_min=budget_min,
            budget_max=budget_max,
        )
        return project

    @strawberry.mutation
    def update_project(
        self,
        info,
        id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        budget_min: Optional[Decimal] = None,
        budget_max: Optional[Decimal] = None,
        status: Optional[str] = None,
    ) -> ProjectType:
        user = info.context.request.user
        project = Project.objects.get(pk=id)
        if project.owner != user:
            raise Exception("Not permitted")
        if title is not None:
            project.title = title
        if description is not None:
            project.description = description
        if budget_min is not None:
            project.budget_min = budget_min
        if budget_max is not None:
            project.budget_max = budget_max
        if status is not None:
            project.status = status
        project.save()
        return project

    @strawberry.mutation
    def delete_project(self, info, id: int) -> bool:
        user = info.context.request.user
        project = Project.objects.get(pk=id)
        if project.owner != user:
            raise Exception("Not permitted")
        project.delete()
        return True
