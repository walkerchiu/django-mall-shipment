import graphene

from django_app_core.relay.connection import DjangoFilterConnectionField
from django_mall_shipment.graphql.storefront.types.shipment import ShipmentNode


class ShipmentMutation(graphene.ObjectType):
    pass


class ShipmentQuery(graphene.ObjectType):
    shipment = graphene.relay.Node.Field(ShipmentNode)
    shipments = DjangoFilterConnectionField(
        ShipmentNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
