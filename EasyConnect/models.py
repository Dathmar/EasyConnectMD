from django.db import models

# Create your models here.
"""
class Question(models.Model):
    question_text = models.CharField(max_length=200)
    pub_date = models.DateTimeField('date published')


class Choice(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)
"""

class Patient(models.Model):
    first_name = models.CharField()
    last_name = models.CharField()
    phone_number = models.CharField()
    email = models.EmailField()
    dob = models.DateField()

    create_date = models.DateTimeField('date created')
