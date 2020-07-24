from django.contrib import admin
from .models import Product, Plan, Subscription


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'apimode',
        'name', 'description', 'type', 'category',
        'create_time', 'update_time'
    ]
    list_filter = ['apimode', 'type']


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'apimode',
        'product',
        'name', 'description', 'status',
        'create_time', 'update_time'
    ]
    list_filter = ['apimode', 'status']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'apimode',
        'plan',
        'status', 'status_change_note', 'status_update_time',
        'start_time', 'quantity',
        'create_time', 'update_time'
    ]
    list_filter = ['apimode', 'status']
