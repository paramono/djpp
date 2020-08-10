# djpp

## Warning! Not ready for production use yet!

Paypal API integration for Django - features Subscription functionality introduced in PayPal API v2

The main focus of this repository is the implementation of new PayPal Subscriptions API for Django, which is documented [here](https://developer.paypal.com/docs/subscriptions/#), but you can handle regular payments with it too.

## Requirements

- Python 3.5+
- Django 2.0+
- Postgres 9.6+ (Non-postgres engines not supported)

## Repository history

Initially, this package was very loosely based on ``djpaypal`` - it only borrowed Webhooks implementation and defined 3 models that are absent from `djpaypal` - **Product**, **Plan** and **Subscription**. However, soon the main author (@paramono) realized that even if you create a Subscription using the new API, PayPal sends Webhook events for the older models defined in ``djpaypal``. As a result, this library does borrow code from ``djpaypal`` (mainly models), but adds more models, makes it PEP8 compliant, tries to make it more future-proof and prioritizes the new Subscription API - a full list of differences will be provided below.

It also adds some models from PayPal API v2 absent from djpaypal and that aren't directly related to subscriptions - for example, [Order](https://developer.paypal.com/docs/api/orders/v2/#orders) (named CheckoutOrder in this app)
