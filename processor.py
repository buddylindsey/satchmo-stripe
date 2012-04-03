import stripe
import decimal
from django.utils.translation import ugettext_lazy as _

from payment.modules.base import BasePaymentProcessor, ProcessorResult

from forms import StripePayShipForm
from models import StripeToken


class PaymentProcessor(BasePaymentProcessor):
    def __init__(self, settings):
        super(PaymentProcessor, self).__init__('stripe', settings)

    def _load_api_key(self):
        live = self.is_live()

        if live:
            stripe.api_key = self.settings.API_KEY.value
        else:
            stripe.api_key = self.settings.TEST_API_KEY.value

    def _get_payment_token(self, order):
        for payment in order.payments.order_by('-time_stamp'):
            for token in payment.stripe_tokens.all():
                return token
        return None

    def _validate_token(self, token):
        self._load_api_key()

        try:
            stripe_token = stripe.Token.retrieve(token.payment_token)
            return not stripe_token.used
        except Exception, e:
            print("Exception while lookup token %s: %s", token.stripe_token, e)

        return false

    def capture_payment(self, testing=False, order=None, amount=None):
        if not order:
            order = self.order

        if order.paid_in_full:
            self.record_payment()
            return ProcessorResult(self.key, True, _("No charge needed, paid in full"))

        if amount is None:
            amount = order.balance

        token = self._get_payment_token(order)

        if not token:
            return ProcessorResult(self.key, False, _("No valid payment found, Please re-enter your payment information"))

        if not self._validate_token(token):
            payment = self.record_failure(amount=amount, transaction_id=token.payment_token,
                    reason_code='0', details=_("Failed to Validate Stripe token."))

            return ProcessorResult(self.key, False, _("Could not validate payment authorization. Please re-enter your payment information."), payment=payment)

        #stripe token valid
        payment = None
        try:
            amount_cents = int(amount * decimal.Decimal('100'))
            charge = stripe.Charge.create(
                    amount = amount_cents,
                    currency = 'usd',
                    card = token.payment_token,
                    description = u'Order %d for %s' % (order.id, order.contact.email))

            payment = self.record_payment(order=order, amount=amount, transaction_id=charge.id, reason_code='0')
            return ProcessorResult(self.key, True, _('Success'), payment)
        except stripe.InvalidRequestError, e:
            error_code = e.json_body.get('error', {}).get('type', '')
            payment = self.record_failure(amount=amount, transaction_id=token.stripe_token,reason_code=error_code, deatils=e.message)

        if not payment:
            payment = self.record_failure(amount=amount, transaction_id=token.stripe_token, reason_code='0', details=_("Failed to create stripe charge"))

        return ProcessorResult(self.key, False, _('Could not charge your credit card, Please re-enter your payment information.'), payment=payment)






#class PaymentProcessor(BasePaymentProcessor):
#    """
#    Stripe payment processing module
#    You must have a Stripe account to use this module.
#    """
#
#    settings = None
#
#    def __init__(self, settings):
#        self.settings = settings
#        super(PaymentProcessor, self).__init__('stripe', settings)
#
#    def capture_payment(self, testing=False, order=None, amount=None):
#        """
#        Process payments without an authorization step.
#        """
#        if order:
#            self.prepare_data(order)
#        else:
#            order = self.order
#
#        if order.paid_in_full:
#            self.log_extra('%s is paid in full, no capture attempted.', order)
#            results = ProcessorResult(self.key, True, _("No charge needed, paid in full."))
#            self.record_payment()
#        else:
#            self.log_extra("Capturing payment for %s", order)
#
#            # do the stripe stuff here
#            payment = self.record_payment(order=self.order, amount="4.00", transaction_id='1234', reason_code="123")
#            results = ProcessorResult(self.key, True, _("Charged to Stripe"))

#        return results
        

#    def can_authorize(self):
#        return True

#    def can_recur_bill(self):
#        """
#        Stripe can do recuring billing, but it is not
#        yet implemented in this module
#        """
#        return False
