import datetime
import os

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from EasyConnect.forms import PatientForm, SymptomsForm, ProviderForm
from EasyConnect.models import Patient, Symptoms, ProviderNotes

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
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            first_name = form.cleaned_data['first_name']
            last_name = form.cleaned_data['last_name']
            phone_number = form.cleaned_data['phone_number']
            email = form.cleaned_data['email']
            dob = form.cleaned_data['dob']
            gender = form.cleaned_data['gender']
            zip = form.cleaned_data['zip']
            tos = form.cleaned_data['tos']

            patient = Patient(first_name=first_name,
                              last_name=last_name,
                              phone_number=phone_number,
                              email=email,
                              dob=dob,
                              gender=gender,
                              zip=zip,
                              tos=tos)
            patient.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('easyconnect:connect-2', args=(patient.id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        form = PatientForm()

    context = {
        'form': form
    }

    return render(request, 'EasyConnect/connect.html', context)


def connect_2(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)

    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = SymptomsForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            symptom_description = form.cleaned_data['symptom_description']
            allergies = form.cleaned_data['allergies']
            medications = form.cleaned_data['medications']
            previous_diagnosis = form.cleaned_data['previous_diagnosis']

            symptoms = Symptoms(patient=patient_id,
                              symptom_description=symptom_description,
                              allergies=allergies,
                              medications=medications,
                              previous_diagnosis=previous_diagnosis)
            symptoms.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('video-chat', args=(patient_id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        form = SymptomsForm()

    context = {
        'form': form,
        'zip': patient.zip
    }

    return render(request, 'EasyConnect/connect-2.html', context)


def video_chat(request):
    return render(request, 'EasyConnect/VideoChat.html')


def provider_view(request):
    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        form = ProviderForm(request.POST)
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            hpi = form.cleaned_data['hpi']
            #assessments = form.cleaned_data['assessments']
            treatment = form.cleaned_data['treatment']
            followup = form.cleaned_data['followup']
            return_to_work_notes = form.cleaned_data['return_to_work_notes']

            provider_notes = ProviderNotes(hpi=hpi,
                              #assessments=assessments,
                              treatment=treatment,
                              followup=followup,
                              return_to_work_notes=return_to_work_notes)
            provider_notes.save()

            # redirect to a new URL:
            return HttpResponseRedirect('EasyConnect/index.html')

    # If this is a GET (or any other method) create the default form.
    else:
        form = ProviderForm()

    context = {
        'form': form
    }

    return render(request, 'EasyConnect/provider-view.html', context)

