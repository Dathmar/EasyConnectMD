from django.contrib import admin
from .models import Affiliate, Coupon, Patient, Payment

# Register your models here.
admin.site.register(Affiliate)
admin.site.register(Coupon)
admin.site.register(Patient)

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'status', 'create_datetime', 'update_datetime']
    list_filter = ['status', 'create_datetime', 'update_datetime']