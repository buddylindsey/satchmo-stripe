from django.db import models
from django.utils.translation import ugettext as _

from satchmo_store.shop.models import Cart, Order, OrderPayment

import config
PAYMENT_PROCESSOR = True

class StripeToken(models.Model):
    orderpayment = models.ForeignKey(OrderPayment, unique=True, related_name="stripe_tokens")
    payment_token = models.CharField(_("Payment Token"), max_length=128, blank=True, null=True, editable=False)
    display_cc = models.CharField(_("CC Number (Last 4 digits)"), max_length=4,)
