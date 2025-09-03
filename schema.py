import strawberry
import projects.schema
import bids.schema
import reviews.schema
import payments.schema
import chat.schema
import notifications.schema

@strawberry.type
class Query(
    projects.schema.Query,
    bids.schema.Query,
    reviews.schema.Query,
    payments.schema.Query,
    chat.schema.Query,
    notifications.schema.Query,
):
    hello: str = "world"

@strawberry.type
class Mutation(
    projects.schema.Mutation,
    bids.schema.Mutation,
    reviews.schema.Mutation,
    payments.schema.Mutation,
    chat.schema.Mutation,
    notifications.schema.Mutation,
):
    pass

schema = strawberry.Schema(query=Query, mutation=Mutation)
