from django.contrib import admin
from .models import Patient, Preferred_Pharmacy

# Register your models here.
admin.site.register(Patient)
admin.site.register(Preferred_Pharmacy)
