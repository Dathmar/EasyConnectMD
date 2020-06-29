from django.db import models
from EasyConnect.choices import STATE_CHOICES, GENDER_CHOICES
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
class Patient(models.Model):
    # page 1
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    phone_number = PhoneNumberField(blank=False)
    email = models.EmailField(max_length=200)
    dob = models.DateField()
    gender = models.CharField(choices=GENDER_CHOICES, max_length=1, default=None)
    address1 = models.CharField(max_length=200)
    address2 = models.CharField(max_length=200, blank=True)
    city = models.CharField(max_length=200)
    state = models.CharField(choices=STATE_CHOICES, max_length=2)
    zip = models.CharField(max_length=10, default=0)

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
    description = models.TextField()
    allergies = models.TextField()
    medications = models.TextField()
    diabetes = models.BooleanField()
    copd = models.BooleanField()
    cancer = models.BooleanField()
    stroke = models.BooleanField()
    heart_attack = models.BooleanField()
    migraines = models.BooleanField()
    none_of_the_above = models.BooleanField()

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
