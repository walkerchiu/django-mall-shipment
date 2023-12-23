import uuid

from django.conf import settings
from django.db import models

from django_prices.models import MoneyField
from safedelete.models import SOFT_DELETE_CASCADE

from django_app_core.models import (
    CommonDateAndSafeDeleteMixin,
    PublishableModel,
    TranslationModel,
)
from django_app_organization.models import Organization


class Shipment(CommonDateAndSafeDeleteMixin, PublishableModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, models.CASCADE)
    slug = models.CharField(max_length=255, db_index=True)
    sort_key = models.IntegerField(db_index=True, null=True)
    currency = models.CharField(
        max_length=settings.DEFAULT_CURRENCY_CODE_LENGTH,
        default=settings.DEFAULT_CURRENCY_CODE,
    )
    price_amount = models.DecimalField(
        max_digits=settings.DEFAULT_MAX_DIGITS,
        decimal_places=settings.DEFAULT_DECIMAL_PLACES,
        default=0,
    )
    price = MoneyField(amount_field="price_amount", currency_field="currency")

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_shipment_shipment"
        get_latest_by = "updated_at"
        index_together = [
            ["organization", "slug"],
        ]
        unique_together = [["organization", "slug"]]
        ordering = ["sort_key"]

    def __str__(self):
        return str(self.id)


class ShipmentTrans(CommonDateAndSafeDeleteMixin, TranslationModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    shipment = models.ForeignKey(
        Shipment, related_name="translations", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=255, db_index=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    content_checkout = models.TextField(blank=True, null=True)

    _safedelete_policy = SOFT_DELETE_CASCADE

    class Meta:
        db_table = settings.APP_NAME + "_shipment_shipment_trans"
        get_latest_by = "updated_at"
        index_together = (("language_code", "shipment"),)
        ordering = ["language_code"]

    def __str__(self):
        return str(self.id)
