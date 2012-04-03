import logging
from django import forms
from django.utils.translation import ugettext as _

from payment import signals
from payment.forms import SimplePayShipForm

from satchmo_store.contact.models import Contact
from satchmo_store.shop.models import Cart, Order, OrderPayment
from models import StripeToken

from signals_ahoy.signals import form_presave, form_postsave

log = logging.getLogger('payment.stripe.forms')

class StripePayShipForm(SimplePayShipForm):
    stripe_token = forms.CharField(max_length=50, widget=forms.HiddenInput({"value":""}))
    credit_number = forms.CharField(required=False)
    credit_type = forms.ChoiceField()

    def __init__(self, request, paymentmodule, *args, **kwargs):
        creditchoices = paymentmodule.CREDITCHOICES.choice_values
        super(StripePayShipForm, self).__init__(request, paymentmodule, *args, **kwargs)

        self.fields['credit_type'].choices = creditchoices
        self.tempCart = Cart.objects.from_request(request)
        self.the_token = None

        try:
            self.tempContact = Contact.objects.from_request(request)
        except Contact.DoesNotExist:
            self.tempContact = None
        
    def clean_stripe_token(self):
        print('in clean method')
        if len(self.cleaned_data['stripe_token']) == 0:
            raise forms.ValidationError(_('Invalid Stripe Token'))

        return self.cleaned_data['stripe_token']

    def save(self, request, cart, contact, payment_module, data=None):
        form_presave.send(StripePayShipForm, form=self)
        print('after presave')
        if data is None:
            data = self.cleaned_data
        assert(data)
        super(StripePayShipForm, self).save(request, cart, contact, payment_module, data=data)

        print('after super')
        if self.orderpayment:
            print('in orderpayment')
            op = self.orderpayment.capture
            token = StripeToken(
                orderpayment=op,
                payment_token = data['stripe_token'],)
            token.save()
            self.the_token = token
        form_postsave.send(StripePayShipForm, form=self)
