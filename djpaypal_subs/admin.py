from django.contrib import admin
from django.utils.html import format_html

from .models import Product, Plan, Subscription, WebhookEvent, WebhookEventTrigger
from .settings import PAYPAL_SUBS_WEBHOOK_ID


class BasePaypalModelAdmin(admin.ModelAdmin):
    _common_fields = ("id", "date_created", "date_modified", "apimode", )
    # change_form_template = "djpaypal/admin/change_form.html"

    def get_fieldsets(self, request, obj=None):
        # Have to remove the fields from the common set, otherwise they'll show up twice.
        fields = [f for f in self.get_fields(request, obj) if f not in self._common_fields]
        return (
            (None, {"fields": self._common_fields}),
            (self.model.__name__, {"fields": fields}),
        )

    def get_list_display(self, request):
        return ("__str__", ) + self.list_display + self._common_fields[1:]

    def get_list_filter(self, request):
        return self.list_filter + ("apimode", )

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + self._common_fields

    def get_search_fields(self, request):
        return self.search_fields + ("id", )

    def has_add_permission(self, request):
        return False


@admin.register(Product)
class ProductAdmin(BasePaypalModelAdmin):
    list_display = (
        'id', 'apimode',
        'name', 'description', 'type', 'category',
        'create_time', 'update_time',
    )
    list_filter = ('apimode', 'type', )


@admin.register(Plan)
class PlanAdmin(BasePaypalModelAdmin):
    list_display = (
        'id', 'apimode',
        'product',
        'name', 'description', 'status',
        'create_time', 'update_time',
    )
    list_filter = ('apimode', 'status', )
    raw_id_fields = ('product', )


@admin.register(Subscription)
class SubscriptionAdmin(BasePaypalModelAdmin):
    list_display = (
        'id', 'apimode',
        'plan',
        'status', 'status_change_note', 'status_update_time',
        'start_time', 'quantity',
        'create_time', 'update_time',
    )
    list_filter = ('apimode', 'status', )
    raw_id_fields = ('plan', )


@admin.register(WebhookEvent)
class WebhookEventAdmin(BasePaypalModelAdmin):
    list_display = ("event_type", "resource_type", "resource_id_link", "create_time", )
    list_filter = ("create_time", "event_type", )
    ordering = ("-create_time", )
    readonly_fields = (
        "summary", "event_type", "resource_type", "resource_id_link", "create_time",
        "event_version", "resource", "status", "transmissions",
    )
    search_fields = ("resource_id", )

    def resource_id_link(self, obj):
        return format_html(
            '<strong><a href="{}">{}</a></strong>',
            obj.get_resource().admin_url,
            obj.resource_id,
        )
    resource_id_link.short_description = "Resource Id"


@admin.register(WebhookEventTrigger)
class WebhookEventTriggerAdmin(admin.ModelAdmin):
    list_display = (
        "date_created", "date_modified", "valid", "processed", "exception", "webhook_event",
    )
    list_filter = ("date_created", "valid", "processed", )
    raw_id_fields = ("webhook_event", )

    def reverify(self, request, queryset):
        for trigger in queryset:
            if trigger.verify(webhook_id=PAYPAL_SUBS_WEBHOOK_ID):
                trigger.valid = True
                trigger.save()

    def reprocess(self, request, queryset):
        for trigger in queryset:
            if not trigger.valid:
                # Skip invalid webhooks (never process them)
                continue
            trigger.process()

        def has_add_permission(self, request):
            return False

    actions = (reverify, reprocess)
