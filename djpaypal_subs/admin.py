from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone

from . import models
from .settings import PAYPAL_SUBS_WEBHOOK_ID


class BasePaypalModelAdmin(admin.ModelAdmin):
    _common_fields = ("id", "date_created", "date_modified", "livemode", )
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
        return self.list_filter + ("livemode", )

    def get_readonly_fields(self, request, obj=None):
        return self.readonly_fields + self._common_fields

    def get_search_fields(self, request):
        return self.search_fields + ("id", )

    def has_add_permission(self, request):
        return False


@admin.register(models.BillingPlan)
class BillingPlanAdmin(BasePaypalModelAdmin):
    list_display = ("state", "type", "create_time")
    list_filter = ("type", "state", "create_time", "update_time")
    raw_id_fields = ("payment_definitions", )

    def activate_plans(self, request, queryset):
        for obj in queryset:
            obj.activate()

    actions = (activate_plans, )


@admin.register(models.BillingAgreement)
class BillingAgreementAdmin(BasePaypalModelAdmin):
    list_display = ("user", "state")
    list_filter = ("state", )
    raw_id_fields = ("user", "payer_model")

    def cancel(self, request, queryset):
        for agreement in queryset:
            agreement.cancel(note="Cancelled by admin", immediately=False)
    cancel.short_description = "Cancel selected agreements at end of billing period"

    def cancel_immediately(self, request, queryset):
        for agreement in queryset:
            agreement.cancel(note="Cancelled by admin", immediately=True)
    cancel_immediately.short_description = "Cancel selected agreements immediately"

    def expire(self, request, queryset):
        for agreement in queryset:
            agreement.end_of_period = timezone.now()
            agreement.save()
    expire.short_description = "Mark selected agreements as expired"

    actions = (cancel, cancel_immediately, expire)


@admin.register(models.PreparedBillingAgreement)
class PreparedBillingAgreementAdmin(admin.ModelAdmin):
    list_display = (
        "__str__", "livemode", "user", "executed_agreement", "executed_at",
        "created", "updated"
    )
    list_filter = ("livemode", "executed_at")
    readonly_fields = ("id", "created", "updated")
    raw_id_fields = ("user", "executed_agreement")

    def has_add_permission(self, request):
        return False


@admin.register(models.ChargeModel)
class ChargeModelAdmin(BasePaypalModelAdmin):
    list_display = ("type", )
    list_filter = ("type", )


@admin.register(models.Dispute)
class DisputeAdmin(BasePaypalModelAdmin):
    list_display = ("status", "reason", "create_time")
    list_filter = ("status", "reason")
    ordering = ("-create_time", )
    readonly_fields = (
        "create_time", "update_time", "disputed_transactions", "reason",
        "dispute_amount", "dispute_outcome", "seller_response_due_date",
        "dispute_flow"
    )


@admin.register(models.Payer)
class PayerAdmin(admin.ModelAdmin):
    list_display = (
        "__str__", "first_name", "last_name", "email", "user", "livemode"
    )
    search_fields = ("id", "first_name", "last_name", "email")
    raw_id_fields = ("user", )

    def has_add_permission(self, request):
        return False


@admin.register(models.PaymentDefinition)
class PaymentDefinitionAdmin(BasePaypalModelAdmin):
    list_display = (
        "type", "frequency", "frequency_interval", "cycles",
    )
    list_filter = ("type", "frequency")
    raw_id_fields = ("charge_models", )


@admin.register(models.Refund)
class RefundAdmin(BasePaypalModelAdmin):
    date_hierarchy = "create_time"
    list_display = (
        "state", "invoice_number", "refund_reason_code", "create_time",
    )
    list_filter = ("refund_reason_code", )
    raw_id_fields = ("sale", "parent_payment")
    ordering = ("-create_time", )
    readonly_fields = (
        "state", "sale", "parent_payment", "refund_reason_code",
        "refund_funding_type", "create_time", "update_time",
    )


@admin.register(models.Sale)
class SaleAdmin(BasePaypalModelAdmin):
    date_hierarchy = "create_time"
    list_display = ("state", "create_time", "update_time")
    list_filter = ("state", "payment_mode")
    raw_id_fields = ("billing_agreement", "parent_payment")
    ordering = ("-create_time", )
    readonly_fields = (
        "amount", "payment_mode", "state", "reason_code",
        "protection_eligibility", "protection_eligibility_type",
        "clearing_time", "transaction_fee", "receivable_amount",
        "exchange_rate", "fmf_details", "receipt_id", "parent_payment",
        "processor_response", "billing_agreement", "soft_descriptor",
        "create_time", "update_time",
    )
    search_fields = ("receipt_id", )


@admin.register(models.CheckoutOrder)
class CheckoutOrderAdmin(BasePaypalModelAdmin):
    date_hierarchy = 'create_time'
    list_display = ('intent', 'status', 'create_time', 'update_time')
    list_filter = ('intent', 'status')
    # raw_id_fields = ("billing_agreement", "parent_payment")
    ordering = ('-create_time', )
    readonly_fields = (
        'payment_source', 'intent', 'payer', 'purchase_units', 'status',
        'create_time', 'update_time',
    )
    search_fields = ('id', )


@admin.register(models.Product)
class ProductAdmin(BasePaypalModelAdmin):
    list_display = (
        'id', 'livemode', 'name', 'description', 'type', 'category',
        'create_time', 'update_time',
    )
    list_filter = ('livemode', 'type', )


@admin.register(models.Plan)
class PlanAdmin(BasePaypalModelAdmin):
    list_display = (
        'id', 'livemode',
        'product',
        'name', 'description', 'status',
        'create_time', 'update_time',
    )
    list_filter = ('livemode', 'status', )
    raw_id_fields = ('product', )


@admin.register(models.Subscription)
class SubscriptionAdmin(BasePaypalModelAdmin):
    list_display = (
        'id', 'livemode',
        'plan',
        'status', 'status_change_note', 'status_update_time',
        'start_time', 'quantity',
        'create_time', 'update_time',
    )
    list_filter = ('livemode', 'status', )
    raw_id_fields = ('plan', )


@admin.register(models.WebhookEvent)
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


@admin.register(models.WebhookEventTrigger)
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
