from django.db import models

from .base import PaypalModel
from ..constants import (
    ORDER_INTENT_CHOICES, ORDER_STATUS_CHOICES,
    CAPTURE_STATUS_CHOICES, DISBURSEMENT_MODE_CHOICES,
)
from ..fields import JSONField, CurrencyAmountField


class CheckoutOrder(PaypalModel):
    '''
    This model is called simply "Order" in PayPal docs, but Paypal calls this resource
    'checkout-order'
    '''

    payment_source = JSONField(default=dict)
    intent = models.CharField(choices=ORDER_INTENT_CHOICES, max_length=24)
    payer = JSONField(default=dict)
    purchase_units = JSONField(default=list)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=24)


class Capture(PaypalModel):
    '''
    https://developer.paypal.com/docs/api/orders/v2/#definition-capture
    This resource is sent to webhook when you try to capture CheckoutOrder
    '''
    status = models.CharField(choices=CAPTURE_STATUS_CHOICES, max_length=24)
    status_details = JSONField()
    amount = CurrencyAmountField()

    invoice_id = models.CharField(max_length=255)
    custom_id  = models.CharField(max_length=127)

    seller_protection = JSONField()
    final_capture = models.BooleanField()
    seller_receivable_breakdown = JSONField()

    disbursement_mode = models.CharField(choices=DISBURSEMENT_MODE_CHOICES, blank=True)
    supplementary_data = JSONField(default=dict)
