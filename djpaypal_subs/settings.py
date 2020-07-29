from django.conf import settings

PAYPAL_SUBS_CLIENT_ID = getattr(settings, "PAYPAL_SUBS_CLIENT_ID", None)
PAYPAL_SUBS_SECRET    = getattr(settings, "PAYPAL_SUBS_SECRET", None)

PAYPAL_SUBS_MODE       = getattr(settings, "PAYPAL_SUBS_MODE", 'sandbox')  # or 'live'
PAYPAL_SUBS_WEBHOOK_ID = getattr(settings, 'PAYPAL_SUBS_WEBHOOK_ID', None)

PAYPAL_SUBS_API_BASE_URL_SANDBOX = getattr(settings, 'PAYPAL_SUBS_API_BASE_URL_SANDBOX',
                                           'https://api.sandbox.paypal.com')
PAYPAL_SUBS_API_BASE_URL_LIVE    = getattr(settings, 'PAYPAL_SUBS_API_BASE_URL_LIVE',
                                           'https://api.paypal.com')

if PAYPAL_SUBS_MODE == 'sandbox':
    PAYPAL_SUBS_API_BASE_URL = PAYPAL_SUBS_API_BASE_URL_SANDBOX
elif PAYPAL_SUBS_MODE == 'live':
    PAYPAL_SUBS_API_BASE_URL = PAYPAL_SUBS_API_BASE_URL_LIVE

PAYPAL_SETTINGS = {
    "mode": PAYPAL_SUBS_MODE,
    "client_id": PAYPAL_SUBS_CLIENT_ID,
    "client_secret": PAYPAL_SUBS_SECRET,
}

if PAYPAL_SUBS_CLIENT_ID and PAYPAL_SUBS_SECRET:
    from paypalrestsdk import configure
    configure(PAYPAL_SETTINGS)
