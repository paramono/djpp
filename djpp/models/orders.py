from django.db import models

from .base import PaypalModel
from ..constants import (
    ORDER_INTENT_CHOICES, ORDER_STATUS_CHOICES,
    CAPTURE_STATUS_CHOICES, DISBURSEMENT_MODE_CHOICES,
)
from ..fields import JSONField, CurrencyAmountField


class CheckoutOrder(PaypalModel):
    '''
    https://developer.paypal.com/docs/api/orders/v2/#orders

    This model is called simply "Order" in PayPal docs, but Paypal calls this resource
    'checkout-order'
    '''

    payment_source = JSONField(default=dict)
    intent = models.CharField(choices=ORDER_INTENT_CHOICES, max_length=24)
    payer = JSONField(default=dict)
    purchase_units = JSONField(default=list)
    status = models.CharField(choices=ORDER_STATUS_CHOICES, max_length=24)
    payer_model = models.ForeignKey(
        'Payer', on_delete=models.SET_NULL, null=True, blank=True,
    )

    def save(self, **kwargs):
        from .payer import Payer

        # On save, get the payer_info object and do a best effort attempt at
        # saving a Payer model and relation into the db.
        payer_info = self.payer.get('payer_info', {})
        if payer_info and 'payer_id' in payer_info:
            # Copy the payer_info dict before mutating it
            payer_info = payer_info.copy()
            payer_id = payer_info.pop('payer_id')
            payer_info['user'] = self.user
            payer_info['livemode'] = self.livemode
            self.payer_model, created = Payer.objects.update_or_create(
                id=payer_id, defaults=payer_info
            )
        return super().save(**kwargs)


class Capture(PaypalModel):
    '''
    https://developer.paypal.com/docs/api/orders/v2/#definition-capture

    This resource is sent to webhook when you try to capture CheckoutOrder
    '''
    status = models.CharField(choices=CAPTURE_STATUS_CHOICES, max_length=24)
    status_details = JSONField(default=dict)
    amount = CurrencyAmountField()

    invoice_id = models.CharField(max_length=255, blank=True)
    custom_id  = models.CharField(max_length=127, blank=True)

    seller_protection = JSONField()
    final_capture = models.BooleanField()
    seller_receivable_breakdown = JSONField()

    disbursement_mode = models.CharField(choices=DISBURSEMENT_MODE_CHOICES,
                                         max_length=24, blank=True)
    supplementary_data = JSONField(default=dict)
