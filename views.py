from django.views.decorators.cache import never_cache
from django import http

from satchmo_store.shop.models import Cart
from satchmo_store.shop.models import Order, OrderPayment
from satchmo_utils.dynamic import lookup_url, lookup_template

from livesettings import config_get_group
from payment.views import confirm, payship
from satchmo_stripe.forms import StripePayShipForm

stripe = config_get_group('PAYMENT_SATCHMO_STRIPE')

def stripe_pay_ship_process_form(request, contact, working_cart, payment_module, allow_skip=True, *args, **kwargs):
    def _get_form(request, payment_module, *args, **kwargs):
        return StripePayShipForm(request, payment_module, *args, **kwargs) 

    if request.method == "POST":
        new_data = request.POST.copy()

        form = _get_form(request, payment_module, new_data, *args, **kwargs)
        if form.is_valid():
            data = form.cleaned_data
            form.save(request, working_cart, contact, payment_module, data=data)
            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))
        else:
            pass
    else:
        order_data = {}
        try:
            order = Order.objects.from_request(request)
            if order.shipping_model:
                order_data['shipping'] = order.shipping_model
            if order.credit_card:
                # check if valid token
                pass

            kwargs['initial'] = order_data
            ordershippable = order.is_shippable
        except Order.DoesNotExist:
            pass

        form = _get_form(request, payment_module, *args, **kwargs)
        if not form.is_needed():
            form.save(request, working_cart, contact, None, data={'shipping', form.shipping_dict.keys()[0]})

            url = lookup_url(payment_module, 'satchmo_checkout-step3')
            return (True, http.HttpResponseRedirect(url))

    return (False, form)


def pay_ship_info(request):
    return payship.base_pay_ship_info(request, stripe, stripe_pay_ship_process_form, "satchmo_stripe/pay_ship.html")
pay_ship_info = never_cache(pay_ship_info)

def confirm_info(request):
    return confirm.credit_confirm_info(request, stripe)
confirm_info = never_cache(confirm_info)
