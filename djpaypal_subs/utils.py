from django.conf import settings

import requests

from .constants import (
    APIMODE_SANDBOX, APIMODE_LIVE,
    PAYPAL_API_BASE_URL_SANDBOX, PAYPAL_API_BASE_URL_LIVE, PAYPAL_API_BASE_URL,
)


class classproperty(object):
    def __init__(self, f):
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class PaypalApi(object):
    client_id = settings.PAYPAL_SUBSCRIPTIONS_CLIENT_ID
    secret    = settings.PAYPAL_SUBSCRIPTIONS_SECRET
    _token    = None

    @classproperty
    def token(cls):
        if cls._token:
            return cls._token
        else:
            cls._token = cls.get_api_token()
            return cls._token

    @classmethod
    def build_endpoint(cls, endpoint, mode='settings'):
        if mode == 'settings':
            url = PAYPAL_API_BASE_URL + endpoint
        elif mode == APIMODE_SANDBOX:
            url = PAYPAL_API_BASE_URL_SANDBOX + endpoint
        elif mode == APIMODE_LIVE:
            url = PAYPAL_API_BASE_URL_LIVE + endpoint
        return url

    @classmethod
    def get_api_token(cls, client_id=None, secret=None, mode='settings', **kwargs):
        endpoint = '/v1/oauth2/token'
        url = cls.build_endpoint(endpoint, mode=mode)
        headers = {
            'Accept': 'application/json',
            'Accept-Language': 'en_US',
        }
        data = dict(grant_type='client_credentials')

        client_id = client_id or settings.PAYPAL_SUBSCRIPTIONS_CLIENT_ID
        secret    = secret or settings.PAYPAL_SUBSCRIPTIONS_SECRET

        # print(f'url: {url}')
        # print(f'client_id: {client_id}')
        # print(f'secret: {secret}')

        r = requests.post(url, headers=headers, data=data, auth=(client_id, secret))
        r.raise_for_status()
        dic = r.json() or {}
        return dic.get('access_token')

    @classmethod
    def list(cls, endpoint, mode='settings', **kwargs):
        url = cls.build_endpoint(endpoint, mode=mode)
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer %s' % cls.token,
        }
        r = requests.get(url, headers=headers)
        r.raise_for_status()
        return r.json()

    @classmethod
    def list_products(cls, mode='settings', **kwargs):
        endpoint = '/v1/catalogs/products'
        return cls.list(endpoint, mode=mode, **kwargs)

    @classmethod
    def list_plans(cls, mode='settings', **kwargs):
        endpoint = '/v1/billing/plans'
        return cls.list(endpoint, mode=mode, **kwargs)


def get_api_token(client_id=None, secret=None, mode='settings'):
    endpoint = '/v1/oauth2/token'
    if mode == 'settings':
        url = PAYPAL_API_BASE_URL + endpoint
    elif mode == APIMODE_SANDBOX:
        url = PAYPAL_API_BASE_URL_SANDBOX + endpoint
    elif mode == APIMODE_LIVE:
        url = PAYPAL_API_BASE_URL_LIVE + endpoint

    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
    }
    data = dict(grant_type='client_credentials')

    client_id = client_id or settings.PAYPAL_SUBSCRIPTIONS_CLIENT_ID
    secret    = secret or settings.PAYPAL_SUBSCRIPTIONS_SECRET

    r = requests.post(url, headers=headers, data=data, auth=(client_id, secret))
    r.raise_for_status()
    dic = r.json() or {}
    return dic.get('access_token')
