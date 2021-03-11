import uuid
from django.db import models
from EasyConnect.choices import GENDER_CHOICES, DIAGNOSED_CHOICES
from phonenumber_field.modelfields import PhoneNumberField
from django.conf import settings


# Create your models here.
class Affiliate(models.Model):
    affiliate_name = models.TextField()
    affiliate_logo = models.TextField()
    affiliate_url = models.TextField(null=True)
    affiliate_price = models.TextField()

    def __str__(self):
        return self.affiliate_name


class Patient(models.Model):
    # page 1
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_number = PhoneNumberField(max_length=20, blank=False)
    email = models.EmailField(max_length=200)
    dob = models.DateField()
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, default=None)
    zip = models.CharField(max_length=10, default=0)
    tos = models.BooleanField(default=None)
    affiliate = models.ForeignKey(Affiliate, null=True, on_delete=models.PROTECT)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Coupon(models.Model):
    code = models.CharField(max_length=200, default=None)
    begin_date = models.DateField(default=None)
    end_date = models.DateField(default=None)
    discount = models.CharField(max_length=200, default=None)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.code

class Patient_Cost(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    cost = models.CharField(max_length=200, default=None)
    coupon_applied = models.CharField(max_length=1, default='N')


class Preferred_Pharmacy(models.Model):
    # section in page 1
    # would like to expand to location information from Google
    # probably just store the google location data in that case.
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    pharmacy_name = models.CharField(max_length=200, default=None)
    pharmacy_address = models.CharField(max_length=2000, default=None)
    pharmacy_phone = models.CharField(max_length=200, default=None)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.pharmacy_name


class Symptoms(models.Model):
    # page 2
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    symptom_description = models.TextField(default=None)
    allergies = models.TextField(default=None)
    medications = models.TextField(default=None)
    previous_diagnosis = models.CharField(default=None, max_length=2000)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    class Meta:
        verbose_name_plural = 'Symptoms'

    def __str__(self):
        return str(self.patient.id)


class Payment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    nonce = models.CharField(default=None, max_length=2000)
    status = models.CharField(default=None, max_length=200)
    response = models.CharField(default=None, max_length=10000)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)


class Icd10(models.Model):
    IDC10_CDE = models.CharField(max_length=10)
    ICD10_DSC = models.CharField(max_length=500)

    def __str__(self):
        return self.ICD10_DSC

class ProviderNotes(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    hpi = models.TextField(default=None)
    assessments = models.ManyToManyField(Icd10, blank=True)
    treatment = models.TextField(default=None)
    followup = models.TextField(default=None)
    return_to_work_notes = models.TextField(default=None)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)


class Appointments(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.PROTECT)
    status = models.TextField(default=None)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)
    last_update_user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                         related_name='%(class)s_updated', null=True)
    seen_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
                                related_name='%(class)s_seen_by', null=True)

    def __str__(self):
        return self.patient.id
