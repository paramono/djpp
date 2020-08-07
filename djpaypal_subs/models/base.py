from django.contrib.postgres.fields import JSONField
from django.db import models
from django.urls import reverse
from django.utils.decorators import classproperty

from djpaypal_subs.api import PaypalApi
from djpaypal_subs.constants import APIMODE_CHOICES
from djpaypal_subs.settings import PAYPAL_SUBS_LIVEMODE


class PaypalModel(models.Model):
    '''Defines common fields for all models'''
    class Meta:
        abstract = True

    # List of fields that don't show up in cls._meta.get_fields() but are required
    # for proper assignment of values returned from API; mainly used for accesing
    # ForeignKey fields by field_id DeferredAttribute (see field_names() below)
    deferred_attrs = None  # ['product_id'], ['plan_id'], etc

    id = models.CharField(primary_key=True, db_index=True, max_length=50)
    livemode = models.BooleanField(
        null=True,
        default=None,
        blank=True,
        help_text='Null here indicates that the livemode status is unknown or was '
        'previously unrecorded. Otherwise, this field indicates whether this record '
        'comes from Stripe test mode or live mode operation.',
    )

    # These datetimes are synced from Paypal API
    create_time = models.DateTimeField(blank=True, null=True)
    update_time = models.DateTimeField(blank=True, null=True)

    links = JSONField(default=list)

    # These datetimes are handled by django automatically
    date_created = models.DateTimeField(auto_now_add=True)
    date_modified = models.DateTimeField(auto_now=True)

    # Sometimes PayPal returns undocumented fields. These will be extracted
    # into this JSON field - useful if PayPal changes their response json
    _extra_fields = JSONField(default=dict)

    id_field_name = "id"

    def __str__(self):
        if hasattr(self, "name") and self.name:
            return self.name
        return self.id

    @classproperty
    def field_names(cls):
        '''
        Returns list of field names, including some explicitly defined deferred
        attrs like product_id or plan_id
        '''
        if not isinstance(cls.deferred_attrs, list):
            cls.deferred_attrs = []
        return [field.name for field in cls._meta.get_fields()] + cls.deferred_attrs

    @classmethod
    def init_from_api(cls, mode='settings', detailed=True, **kwargs):
        obj_json = PaypalApi.list(cls.endpoint, mode=mode)

        plural = cls.__name__.lower() + 's'
        obj_list = obj_json.get(plural, [])

        for obj in obj_list:
            pk = obj.pop('id')
            if detailed:
                # when you list_objucts, not all the fields will be returned by API,
                # so get the remaining fields one by one
                obj_details = PaypalApi.get(cls.endpoint, pk)
                obj_details.pop('id')
            else:
                obj_details = obj

            obj_details = cls.make_dict_with_defined_fields(obj_details)
            cls.objects.update_or_create(pk=pk, **obj_details)

    @classmethod
    def make_dict_with_defined_fields(cls, obj_details):
        '''
        Sometimes, PayPal returns fields not mentioned in their official
        documentation. Since update_or_create raises an Error when you
        try to insert a field that doesn't exist in a model, it's safer
        to pop non-existing fields from obj_details and insert them into
        a separate JSONField.
        '''
        _extra_fields = {}
        field_names = cls.field_names

        items = list(obj_details.items())
        for item in items:
            print(item)

        for k, v in list(obj_details.items()):
            if k not in field_names:
                _extra_fields.update(k=v)
                obj_details.pop(k)
        obj_details['_extra_fields'] = _extra_fields
        return obj_details

    @staticmethod
    def sdk_object_as_dict(obj):
        if isinstance(obj, dict):
            return obj.copy()
        # Paypal SDK object
        return obj.to_dict()

    @classmethod
    def clean_api_data(cls, data):
        cleaned_data = cls.sdk_object_as_dict(data)

        # Delete links (only useful in the API itself)
        # if "links" in cleaned_data:
        #     del cleaned_data["links"]

        # Extract the ID to return it separately
        id = cleaned_data.pop(cls.id_field_name)
        livemode = cls.extract_livemode(data)

        # Set the livemode; if failed to extract it from data,
        # set the value from settings
        cleaned_data["livemode"] = livemode or PAYPAL_SUBS_LIVEMODE
        return id, cleaned_data, {}

    @classmethod
    def extract_livemode(cls, data):
        '''Tried to extract livemode from links'''
        links = data.get('links', [])
        if not links:
            return None

        url = links[0].get('href', '')
        if 'api.sandbox.paypal.com' in url:
            return False
        elif 'api.paypal.com' in url:
            return True
        return None

    @classmethod
    def get_or_update_from_api_data(cls, data, always_sync=False):
        id, cleaned_data, m2ms = cls.clean_api_data(data)
        cleaned_data = cls.make_dict_with_defined_fields(cleaned_data)
        db_obj, created = cls.objects.get_or_create(**{
            cls.id_field_name: id,
            "defaults": cleaned_data,
        })
        if always_sync or not created:
            db_obj.sync_data(cleaned_data)
            db_obj.save()

        for field, objs in m2ms.items():
            for obj in objs:
                getattr(db_obj, field).add(obj)
        return db_obj, created

    @classmethod
    def find_and_sync(cls, id):
        obj = cls.paypal_model.find(id)
        db_obj, created = cls.get_or_update_from_api_data(obj, always_sync=True)
        return db_obj

    @property
    def admin_url(self):
        return reverse(
            "admin:{app_label}_{model_name}_change".format(
                app_label=self._meta.app_label, model_name=self._meta.model_name
            ),
            args=(self.id, )
        )

    @property
    def dashboard_url(self):
        if self.livemode:
            paypal_url = "https://www.paypal.com"
        else:
            paypal_url = "https://www.sandbox.paypal.com"

        return self.dashboard_url_template.format(
            paypal=paypal_url, webscr=paypal_url + "/cgi-bin/webscr",
            id=getattr(self, self.id_field_name)
        )

    def _sync_data_field(self, k, v):
        if k == "links":
            return False
        if getattr(self, k) != v:
            setattr(self, k, v)
            return True
        return False

    def find_paypal_object(self):
        return self.paypal_model.find(self.id)

    def sync_data(self, obj):
        obj = self.sdk_object_as_dict(obj)
        updated = False
        for k, v in obj.items():
            if self._sync_data_field(k, v):
                updated = True

        if updated:
            self.save()
