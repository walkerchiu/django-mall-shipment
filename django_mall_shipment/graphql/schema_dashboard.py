import graphene

from django_mall_shipment.graphql.dashboard.shipment import (
    ShipmentMutation,
    ShipmentQuery,
)


class Mutation(
    ShipmentMutation,
    graphene.ObjectType,
):
    pass


class Query(
    ShipmentQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
