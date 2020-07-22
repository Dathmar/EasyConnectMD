from django.contrib import admin
from .models import Patient, Preferred_Pharmacy, Symptoms

# Register your models here.
admin.site.register(Patient)
admin.site.register(Preferred_Pharmacy)
admin.site.register(Symptoms)
