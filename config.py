from livesettings import *
from django.utils.translation import ugettext_lazy as _
from django.conf import settings

gettext = lambda s: s
_strings = (gettext('CreditCard'), gettext('Credit Card'))

PAYMENT_GROUP = ConfigurationGroup('PAYMENT_SATCHMO_STRIPE',
        _('Stripe Payment Settings'),
        ordering=102)

config_register_list(
    BooleanValue(PAYMENT_GROUP,
        'LIVE',
        description=_("Accept real payments"),
        help_text=_("False if you want to be in test mode"),
        default=False),

    ModuleValue(PAYMENT_GROUP,
        'MODULE',
        description = _("Implementation Module"),
        hidden = True,
        default = 'satchmo_stripe'),

    StringValue(PAYMENT_GROUP,
        'KEY',
        description=_("Module Key"),
        hidden=True,
        default="SATCHMO_STRIPE"),

    StringValue(PAYMENT_GROUP,
        'LABEL',
        description=_('English name for this group on the checkout screens'),
        default = 'Credit Cards',
        help_text = _('This will be passed to the translation utility')),

    StringValue(PAYMENT_GROUP,
        'URL_BASE',
        description=_('The url base used for constructing urlpatterns which will use this module'),
        default = r'^credit/'),

    StringValue(PAYMENT_GROUP,
        'API_KEY',
        description=_('The API KEY for stripe payment processor'),
        default=""),

    MultipleStringValue(PAYMENT_GROUP,
        'CREDITCHOICES',
        description=_('Available credit cards'),
        choices = (
            (('Amex', 'American Express')),
            (('Visa','Visa')),
            (('Mastercard','Mastercard')),
            (('Discover','Discover'))),
        default = ('Visa', 'Mastercard', 'Discover', 'Amex')),
    
    BooleanValue(PAYMENT_GROUP,
        'CAPTURE',
        description=_('Capture Payment immediately?'),
        default=True,
        help_text=_('IMPORTANT: If false, a capture attempt will be made when the order is marked as shipped')),


    BooleanValue(PAYMENT_GROUP,
        'EXTRA_LOGGING',
        description=_("Verbose logs"),
        help_text=_("Add extensive logs during post."),
        default=False)
)
