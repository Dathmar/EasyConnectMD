import datetime
import os

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from EasyConnect.forms import PatientForm, SymptomsForm
from EasyConnect.models import Patient, Preferred_Pharmacy, Symptoms

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Create your views here.
def index(request):
    return render(request, 'EasyConnect/index.html')


def our_story(request):
    return render(request, 'EasyConnect/our-story.html')


def faq(request):
    return render(request, 'EasyConnect/faq.html')


def privacy_policy(request):
    return render(request, 'EasyConnect/privacy-policy.html')


def connect(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = PatientForm(request.POST)
        print('method == post')
        print('form is_valid == ' + str(form.is_valid()))
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            zip = form.cleaned_data['zip']
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            tos = form.cleaned_data['tos']

            patient = Patient(first_name=first_name,
                              last_name=last_name,
                              phone_number=phone_number,
                              email=email,
                              zip=zip,
                              dob=dob,
                              gender=gender,
                              tos=tos)
            patient.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('easyconnect:connect-2', args=(patient.id,)))

        else:
            print(form.errors)
    # If this is a GET (or any other method) create the default form.
    else:
        print('method != POST')
        form = PatientForm()

    context = {
        'form': form
    }

    return render(request, 'EasyConnect/connect.html', context)


def connect_2(request, id):
    patient = get_object_or_404(Patient, pk=id)
    print(patient)
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = SymptomsForm(request.POST)

        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model fields)
            symptom_description = form.cleaned_data['symptom_description']
            allergies = form.cleaned_data['allergies']
            medications = form.cleaned_data['medications']
            previous_diagnosis = form.cleaned_data['previous_diagnosis']

            symptoms = Symptoms(patient=id,
                              symptom_description=symptom_description,
                              allergies=allergies,
                              medications=medications,
                              previous_diagnosis=previous_diagnosis)
            symptoms.save()

            # pharmacy information
            location_name = form.cleaned_data['location_name']
            pharmacy_phone = form.cleaned_data['pharmacy_phone']

            pharmacy = Preferred_Pharmacy(patient=id,
                                          location_name=location_name,
                                          pharmacy_phone=pharmacy_phone)

            pharmacy.save()
            # redirect to a new URL:
            return HttpResponseRedirect(reverse('video-chat'))

    # If this is a GET (or any other method) create the default form.
    else:
        form = SymptomsForm()

    context = {
        'form': form,
        'patient': patient,
    }

    return render(request, 'EasyConnect/connect-2.html', context)


def video_chat(request, sid):
    return HttpResponse(f"Hello, world. You're at the EasyConnect video chat page with sid {sid}")
