from django.conf import settings
from django.utils.decorators import classproperty

import requests

from .constants import (
    APIMODE_SANDBOX, APIMODE_LIVE,
)
from .settings import (
    PAYPAL_SUBS_CLIENT_ID, PAYPAL_SUBS_SECRET,
    PAYPAL_SUBS_API_BASE_URL_SANDBOX, PAYPAL_SUBS_API_BASE_URL_LIVE, PAYPAL_SUBS_API_BASE_URL,
)


class PaypalApi(object):
    client_id = PAYPAL_SUBS_CLIENT_ID
    secret    = PAYPAL_SUBS_SECRET
    _token    = None

    @classproperty
    def token(cls):
        if cls._token:
            return cls._token
        else:
            cls._token = cls.get_api_token()
            return cls._token

    @classmethod
    def build_endpoint(cls, endpoint, endpoint_id=None, mode='settings'):
        if mode == 'settings':
            url = PAYPAL_SUBS_API_BASE_URL + endpoint
        elif mode == APIMODE_SANDBOX:
            url = PAYPAL_SUBS_API_BASE_URL_SANDBOX + endpoint
        elif mode == APIMODE_LIVE:
            url = PAYPAL_SUBS_API_BASE_URL_LIVE + endpoint

        if endpoint_id:
            url += '/%s' % endpoint_id
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

        client_id = client_id or cls.client_id
        secret    = secret or cls.secret

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
    def get(cls, endpoint, endpoint_id=None, mode='settings', **kwargs):
        if not endpoint_id:
            raise ValueError('Specify endpoint_id to make get details request')
        url = cls.build_endpoint(endpoint, endpoint_id, mode=mode)
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
    def get_product(cls, endpoint_id, mode='settings', **kwargs):
        endpoint = '/v1/catalogs/products'
        return cls.get(endpoint, endpoint_id, mode=mode, **kwargs)

    @classmethod
    def list_plans(cls, mode='settings', **kwargs):
        endpoint = '/v1/billing/plans'
        return cls.list(endpoint, mode=mode, **kwargs)

    @classmethod
    def get_plan(cls, endpoint_id, mode='settings', **kwargs):
        endpoint = '/v1/billing/plans'
        return cls.get(endpoint, endpoint_id, mode=mode, **kwargs)
