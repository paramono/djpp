from django.contrib.postgres.fields import JSONField
from django.db import models

from .constants import (
    APIMODE_CHOICES, PRODUCT_TYPES, PLAN_STATUS_CHOICES,
    SUBSCRIPTION_STATUS_CHOICES,
)


class PaypalModel(models.Model):
    '''Defines common fields for all models'''

    class Meta:
        abstract = True

    id = models.CharField(primary_key=True, db_index=True, max_length=50)
    apimode = models.CharField(choices=APIMODE_CHOICES, max_length=24)

    # These datetimes are synced from Paypal API
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    links = JSONField(default=list)

    # These datetimes are handled by django automatically
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)


class Product(PaypalModel):
    '''https://developer.paypal.com/docs/api/catalog-products/v1/#products'''
    endpoint = '/v1/catalogs/products'

    name = models.CharField(max_length=127)
    description = models.CharField(max_length=256, blank=True)
    type = models.CharField(choices=PRODUCT_TYPES, max_length=24)
    category = models.CharField(max_length=256, blank=True)
    image_url = models.URLField(blank=True, max_length=2000)
    home_url = models.URLField(blank=True, max_length=2000)


class Plan(PaypalModel):
    '''https://developer.paypal.com/docs/api/subscriptions/v1/#plans'''
    endpoint = '/v1/billing/plans'

    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    name = models.CharField(max_length=127)
    status = models.CharField(choices=PLAN_STATUS_CHOICES, max_length=24)
    description = models.CharField(max_length=127, blank=True)

    billing_cycles = JSONField(default=list)  # array
    payment_preferences = JSONField()
    taxes = JSONField()
    quantity_supported = models.BooleanField(default=False)


class Subscription(PaypalModel):
    '''https://developer.paypal.com/docs/api/subscriptions/v1/#subscriptions'''
    endpoint = '/v1/billing/subscriptions'

    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)

    status = models.CharField(choices=SUBSCRIPTION_STATUS_CHOICES, max_length=24)
    status_change_note = models.CharField(max_length=128)
    status_update_time = models.DateTimeField(blank=True, null=True)

    start_time = models.DateTimeField()
    quantity = models.CharField(max_length=32)
    shipping_amount = JSONField()
    subscriber = JSONField()
    billing_info = JSONField()
    application_context = JSONField()  # not returned
