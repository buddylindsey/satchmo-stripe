from django import forms
from django.utils.translation import ugettext as _

from payment import signals
from payment.forms import SimplePayShipForm

from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import Cart, Order, OrderPayment

class StripePayShipForm(SimplePayShipForm):
    stripe_token = forms.CharField(max_length=100, widget=forms.HiddenInput({"value":""}))
    credit_number = forms.CharField(required=False)
    credit_type = forms.ChoiceField()

    def __init__(self, request, paymentmodule, *args, **kwargs):
        creditchoices = paymentmodule.CREDITCHOICES.choice_values
        super(StripePayShipForm, self).__init__(request, paymentmodule, *args, **kwargs)

        self.fields['credit_type'].choices = creditchoices

        self.tempCart = Cart.objects.from_request(request)

        try:
            self.tempContact = Contact.objects.from_request(request)
        except Contact.DoesNotExist:
            self.tempContact = None
        
        

