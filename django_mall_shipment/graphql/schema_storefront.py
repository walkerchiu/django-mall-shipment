import graphene

from django_mall_shipment.graphql.storefront.shipment import ShipmentQuery


class Mutation(
    graphene.ObjectType,
):
    pass


class Query(
    ShipmentQuery,
    graphene.ObjectType,
):
    pass


schema = graphene.Schema(mutation=Mutation, query=Query)
