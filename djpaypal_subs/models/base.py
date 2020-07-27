from django.contrib.postgres.fields import JSONField
from django.db import models
from django.utils.decorators import classproperty

from ..api import PaypalApi
from ..constants import APIMODE_CHOICES


class PaypalModel(models.Model):
    '''Defines common fields for all models'''
    class Meta:
        abstract = True

    # List of fields that don't show up in cls._meta.get_fields() but are required
    # for proper assignment of values returned from API; mainly used for accesing
    # ForeignKey fields by field_id DeferredAttribute (see field_names() below)
    deferred_attrs = None  # ['product_id'], ['plan_id'], etc

    id = models.CharField(primary_key=True, db_index=True, max_length=50)
    apimode = models.CharField(choices=APIMODE_CHOICES, max_length=24)

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

            # Sometimes, PayPal returns fields not mentioned in their official
            # documentation. Since update_or_create raises an Error when you
            # try to insert a field that doesn't exist in a model, it's safer
            # to pop non-existing fields from obj_details and insert them into
            # a separate JSONField.
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
            print('obj_details', obj_details)
            print()

            cls.objects.update_or_create(pk=pk, **obj_details)
