from django.contrib import admin
from .models import Affiliate, Coupon, Patient, Payment, Icd10, UserPhone


admin.site.register(Affiliate)
admin.site.register(Patient)


@admin.register(UserPhone)
class UserPhoneAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone_number']
    list_editable = ['phone_number']


@admin.register(Icd10)
class Icd10Admin(admin.ModelAdmin):
    list_display = ['IDC10_CDE', 'ICD10_DSC']


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ['code', 'discount', 'max_uses', 'current_uses', 'begin_date', 'end_date']


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'patient', 'status', 'create_datetime', 'update_datetime']
    list_filter = ['status', 'create_datetime', 'update_datetime']