from django.core.exceptions import ValidationError
from django.db import transaction

from graphene import ResolveInfo
from graphql_relay import from_global_id
import graphene

from django_app_core.decorators import strip_input
from django_app_core.helpers.translation_helper import TranslationHelper
from django_app_core.relay.connection import DjangoFilterConnectionField
from django_mall_shipment.graphql.dashboard.types.shipment import (
    ShipmentNode,
    ShipmentTransInput,
)
from django_mall_shipment.models import Shipment, ShipmentTrans


class UpdateShipment(graphene.relay.ClientIDMutation):
    class Input:
        id = graphene.ID(required=True)
        sortKey = graphene.Int()
        priceAmount = graphene.Float(required=True)
        isPublished = graphene.Boolean()
        publishedAt = graphene.DateTime()
        translations = graphene.List(
            graphene.NonNull(ShipmentTransInput), required=True
        )

    success = graphene.Boolean()
    shipment = graphene.Field(ShipmentNode)

    @classmethod
    @strip_input
    @transaction.atomic
    def mutate_and_get_payload(cls, root, info: ResolveInfo, **input):
        id = input["id"]
        sortKey = input["sortKey"] if "sortKey" in input else None
        priceAmount = input["priceAmount"]
        isPublished = input["isPublished"] if "isPublished" in input else True
        publishedAt = input["publishedAt"] if "publishedAt" in input else None
        translations = input["translations"]

        translation_helper = TranslationHelper()
        result, message = translation_helper.validate_translations_from_input(
            label="shipment", translations=translations
        )
        if not result:
            raise ValidationError(message)

        if float(priceAmount) < 0:
            raise ValidationError("The priceAmount must be a positive number or zero!")

        try:
            _, shipment_id = from_global_id(id)
        except:
            raise ValidationError("Bad Request!")

        try:
            shipment = Shipment.objects.get(pk=shipment_id)
            shipment.sort_key = sortKey
            shipment.price_amount = priceAmount
            shipment.is_published = isPublished
            shipment.published_at = publishedAt
            shipment.save()

            for translation in translations:
                ShipmentTrans.objects.update_or_create(
                    shipment=shipment,
                    language_code=translation["language_code"],
                    defaults={
                        "name": translation["name"],
                        "description": translation["description"],
                        "content_checkout": translation["content_checkout"],
                    },
                )
        except Shipment.DoesNotExist:
            raise ValidationError("Can not find this shipment!")

        return UpdateShipment(success=True, shipment=shipment)


class ShipmentMutation(graphene.ObjectType):
    shipment_update = UpdateShipment.Field()


class ShipmentQuery(graphene.ObjectType):
    shipment = graphene.relay.Node.Field(ShipmentNode)
    shipments = DjangoFilterConnectionField(
        ShipmentNode,
        orderBy=graphene.List(of_type=graphene.String),
        page_number=graphene.Int(),
        page_size=graphene.Int(),
    )
