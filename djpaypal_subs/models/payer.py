from django.conf import settings
from django.db import models

from ..constants import APIMODE_CHOICES
from ..fields import JSONField


class Payer(models.Model):
    id = models.CharField(max_length=13, primary_key=True)
    first_name = models.CharField(max_length=64, db_index=True, editable=False)
    last_name = models.CharField(max_length=64, db_index=True, editable=False)
    email = models.CharField(max_length=127, db_index=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="paypal_payers",
        help_text="The most recent Django user that transacted as this Payer (best-effort)."
    )
    shipping_address = JSONField(null=True, blank=True, editable=False)
    time_created = models.DateTimeField(null=True, blank=True, editable=False)
    livemode = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text='Null here indicates that the livemode status is unknown or was '
        'previously unrecorded. Otherwise, this field indicates whether this record '
        'comes from Stripe test mode or live mode operation.',
    )
    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "{first_name} {last_name} <{email}>".format(
            first_name=self.first_name, last_name=self.last_name, email=self.email
        )
