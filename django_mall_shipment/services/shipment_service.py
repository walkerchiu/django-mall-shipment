from typing import List, Tuple

from django.db import transaction

from django_app_organization.models import Organization
from django_mall_shipment.models import Shipment


class ShipmentService:
    @transaction.atomic
    def init_default_data(
        self, organization: Organization
    ) -> Tuple[bool, List[Shipment]]:
        items = [
            {
                "slug": "pickup-in-person",
                "sort_key": 1,
                "translations": [
                    {"language_code": "zh-TW", "name": "親自取貨"},
                    {"language_code": "en", "name": "Pickup in Person"},
                ],
            },
            {
                "slug": "direct-shipping",
                "sort_key": 2,
                "translations": [
                    {"language_code": "zh-TW", "name": "直接寄送"},
                    {"language_code": "en", "name": "Direct Shipping"},
                ],
            },
        ]

        results = []
        for item in items:
            shipment, created = Shipment.objects.get_or_create(
                organization=organization, slug=item["slug"], sort_key=item["sort_key"]
            )
            shipment.is_published = True
            shipment.save()

            if created:
                for translation in item["translations"]:
                    shipment.translations.create(
                        language_code=translation["language_code"],
                        name=translation["name"],
                    )

                results.append(shipment)

        return created, results
