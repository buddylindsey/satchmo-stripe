from django.utils.translation import ugettext_lazy as _

from payment.modules.base import BasePaymentProcessor, ProcessorResult

from forms import StripePayShipForm

class PaymentProcessor(BasePaymentProcessor):
    """
    Stripe payment processing module
    You must have a Stripe account to use this module.
    """

    settings = None

    def __init__(self, settings):
        self.settings = settings
        super(PaymentProcessor, self).__init__('stripe', settings)

    def capture_payment(self, testing=False, order=None, amount=None):
        """
        Process payments without an authorization step.
        """
        if order:
            self.prepare_data(order)
        else:
            order = self.order

        if order.paid_in_full:
            self.log_extra('%s is paid in full, no capture attempted.', order)
            results = ProcessorResult(self.key, True, _("No charge needed, paid in full."))
            self.record_payment()
        else:
            self.log_extra("Capturing payment for %s", order)

            # do the stripe stuff here
            payment = self.record_payment(order=self.order, amount="4.00", transaction_id='1234', reason_code="123")
            results = ProcessorResult(self.key, True, _("Charged to Stripe"))

        return results
        

    def can_authorize(self):
        return True

    def can_recur_bill(self):
        """
        Stripe can do recuring billing, but it is not
        yet implemented in this module
        """
        return False


