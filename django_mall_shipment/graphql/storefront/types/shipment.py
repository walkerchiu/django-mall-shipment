import datetime

from django.db.models import Q

from django_filters import CharFilter, FilterSet, OrderingFilter
from django_prices.models import MoneyField
from graphene import ResolveInfo
from graphene_django import DjangoListField, DjangoObjectType
from graphene_django.converter import convert_django_field
import graphene
import graphene_django_optimizer as gql_optimizer

from django_app_core.relay.connection import ExtendedConnection
from django_app_core.types import Money
from django_mall_shipment.models import Shipment, ShipmentTrans


class ShipmentType(DjangoObjectType):
    class Meta:
        model = Shipment
        fields = ()


@convert_django_field.register(MoneyField)
def convert_money_field_to_string(field, registry=None):
    return graphene.Field(Money)


class ShipmentFilter(FilterSet):
    slug = CharFilter(field_name="slug", lookup_expr="exact")

    class Meta:
        model = Shipment
        fields = []

    order_by = OrderingFilter(
        fields=(
            "slug",
            "sort_key",
            "created_at",
            "updated_at",
        )
    )


class ShipmentConnection(graphene.relay.Connection):
    class Meta:
        node = ShipmentType


class ShipmentTransType(DjangoObjectType):
    class Meta:
        model = ShipmentTrans
        fields = (
            "language_code",
            "name",
            "description",
            "content_checkout",
        )


class ShipmentNode(gql_optimizer.OptimizedDjangoObjectType):
    class Meta:
        model = Shipment
        exclude = (
            "currency",
            "price_amount",
            "deleted",
            "deleted_by_cascade",
        )
        filterset_class = ShipmentFilter
        interfaces = (graphene.relay.Node,)
        connection_class = ExtendedConnection

    translations = DjangoListField(ShipmentTransType)

    @classmethod
    def get_queryset(cls, queryset, info: ResolveInfo):
        return (
            queryset.select_related("organization")
            .prefetch_related("translations")
            .filter(
                Q(published_at__lte=datetime.date.today())
                | Q(published_at__isnull=True),
                is_published=True,
            )
        )

    @classmethod
    def get_node(cls, info: ResolveInfo, id):
        return (
            cls._meta.model.objects.select_related("organization")
            .filter(
                Q(published_at__lte=datetime.date.today())
                | Q(published_at__isnull=True),
                is_published=True,
            )
            .filter(pk=id)
            .first()
        )

    @staticmethod
    def resolve_translations(root: Shipment, info: ResolveInfo):
        return root.translations
