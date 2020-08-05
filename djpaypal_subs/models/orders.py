from django.db import models

from .base import PaypalModel
from ..constants import ORDER_INTENT_CHOICES, ORDER_STATUS_CHOICES
from ..fields import JSONField


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
