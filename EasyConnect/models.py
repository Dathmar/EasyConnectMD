import hashlib, random, sys
from django.db import models
from EasyConnect.choices import STATE_CHOICES, GENDER_CHOICES, DIAGNOSED_CHOICES
from phonenumber_field.modelfields import PhoneNumberField


def create_session_hash():
  hash = hashlib.sha1()
  hash.update(str(random.randint(0,sys.maxsize)).encode('utf-8'))
  return hash.hexdigest()


# Create your models here.
class Patient(models.Model):
    # page 1
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_number = PhoneNumberField(blank=False)
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
    location_name = models.CharField(max_length=200)
    pharmacy_phone = models.CharField(max_length=12)

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
    previous_diagnosis = models.CharField(default=None, max_length=255)

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)


class Payment_Response(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    response = models.TextField()

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)


class Video_Chat(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    sid = models.CharField(max_length=200)
    status = models.BooleanField()

    create_datetime = models.DateTimeField('date created', auto_now_add=True)
    update_datetime = models.DateTimeField('date updated', auto_now=True)

    def __str__(self):
        return self.sid
