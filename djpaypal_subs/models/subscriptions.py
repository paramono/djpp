from django.contrib.postgres.fields import JSONField
from django.db import models

from djpaypal_subs.models.base import PaypalModel
from djpaypal_subs.constants import (
    PRODUCTS_ENDPOINT, PRODUCT_TYPES,
    PLANS_ENDPOINT, PLAN_STATUS_CHOICES,
    SUBSCRIPTIONS_ENDPOINT, SUBSCRIPTION_STATUS_CHOICES,
)


class Product(PaypalModel):
    '''https://developer.paypal.com/docs/api/catalog-products/v1/#products'''
    endpoint = PRODUCTS_ENDPOINT

    name = models.CharField(max_length=127)
    description = models.CharField(max_length=256, blank=True)
    type = models.CharField(choices=PRODUCT_TYPES, max_length=24)
    category = models.CharField(max_length=256, blank=True)
    image_url = models.URLField(blank=True, max_length=2000)
    home_url = models.URLField(blank=True, max_length=2000)


class Plan(PaypalModel):
    '''https://developer.paypal.com/docs/api/subscriptions/v1/#plans'''
    endpoint = PLANS_ENDPOINT
    deferred_attrs = ['product_id']

    product = models.ForeignKey('Product', on_delete=models.CASCADE)

    name = models.CharField(max_length=127)
    status = models.CharField(choices=PLAN_STATUS_CHOICES, max_length=24)
    description = models.CharField(max_length=127, blank=True)
    usage_type = models.CharField(max_length=24, blank=True)

    billing_cycles = JSONField(default=list)  # array
    payment_preferences = JSONField()
    taxes = JSONField(blank=True, null=True)
    quantity_supported = models.BooleanField(default=False)


class Subscription(PaypalModel):
    '''https://developer.paypal.com/docs/api/subscriptions/v1/#subscriptions'''
    endpoint = SUBSCRIPTIONS_ENDPOINT
    deferred_attrs = ['plan_id']

    plan = models.ForeignKey('Plan', on_delete=models.CASCADE)

    status = models.CharField(choices=SUBSCRIPTION_STATUS_CHOICES, max_length=24)
    status_change_note = models.CharField(max_length=128, blank=True)
    status_update_time = models.DateTimeField(blank=True, null=True)

    start_time = models.DateTimeField()
    quantity = models.CharField(max_length=32)
    shipping_amount = JSONField(blank=True, null=True)
    subscriber = JSONField(blank=True, null=True)
    billing_info = JSONField(blank=True, null=True)
    application_context = JSONField(blank=True, null=True)  # not returned
