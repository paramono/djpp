# djpaypal_subs

## Warning! Not ready for production use yet!

Paypal Subscriptions integration for Django.

This package implements new PayPal subscriptions API for Django, which is documented here: https://developer.paypal.com/docs/subscriptions/#

Initially, this package was very loosely based on ``djpaypal`` - it only borrowed Webhooks implementation, and defined 3 models that are absent from `djpaypal` - **Product**, **Plan** and **Subscription**. However, soon the main author (@paramono) realized that even if you create a Subscription using the new API, PayPal sends Webhook events for the older models defined in ``djpaypal``. As a result, this library does borrow a lot of code from ``djpaypal`` (mainly models), but makes it PEP8 compliant, tries to make it more future-proof and prioritizes the new Subscription API - a full list of differences will be provided below.
