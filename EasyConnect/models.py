import uuid
from django.db import models
from EasyConnect.choices import GENDER_CHOICES, DIAGNOSED_CHOICES
from phonenumber_field.modelfields import PhoneNumberField


# Create your models here.
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

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'


class Preferred_Pharmacy(models.Model):
    # section in page 1
    # would like to expand to location information from Google
    # probably just store the google location data in that case.
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    pharmacy_name = models.CharField(max_length=200)
    pharmacy_address = models.CharField(max_length=2000)
    pharmacy_phone = models.CharField(max_length=200)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.location_name


class Symptoms(models.Model):
    # page 2
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    symptom_description = models.TextField(default=None)
    allergies = models.TextField(default=None)
    medications = models.TextField(default=None)
    previous_diagnosis = models.CharField(choices=GENDER_CHOICES, default=None, max_length=255)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)


class Payment_Response(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    response = models.TextField()

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)


class Video_Chat(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    status = models.BooleanField()

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.patient.id


class Icd10(models.Model):
    IDC10_CDE = models.CharField(max_length=10)
    ICD10_DSC = models.CharField(max_length=500)


class ProviderNotes(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    hpi = models.TextField(default=None)
    #assessments = models.ManyToManyField(Icd10, blank=True, null=True)
    treatment = models.TextField(default=None)
    followup = models.TextField(default=None)
    return_to_work_notes = models.TextField(default=None)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)
