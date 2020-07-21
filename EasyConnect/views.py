
import os

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse

from EasyConnect.forms import PatientForm, SymptomsForm, ProviderForm, PharmacyForm
from EasyConnect.models import Patient, Symptoms, ProviderNotes, Preferred_Pharmacy, Video_Chat
from square.client import Client

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
        symptom_form = SymptomsForm(request.POST)
        pharmacy_form = PharmacyForm(request.POST)
        if symptom_form.is_valid() and pharmacy_form.is_valid():
            """
            # Instantiate the client
            client = Client(access_token='YOUR ACCESS TOKEN')

            # Call create_customer method to create a new customer
            result = client.customers.create_customer(new_customer)

            # Handle the result
            if result.is_success():
                # Display the response as text
                print(f"Success: {result.text}")
            # Call the error method to see if the call failed
            elif result.is_error():
                print(f"Errors: {result.errors}")
            """

            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            symptom_description = symptom_form.cleaned_data['symptom_description']
            allergies = symptom_form.cleaned_data['allergies']
            medications = symptom_form.cleaned_data['medications']
            previous_diagnosis = symptom_form.cleaned_data['previous_diagnosis']

            symptoms = Symptoms(patient=patient,
                              symptom_description=symptom_description,
                              allergies=allergies,
                              medications=medications,
                              previous_diagnosis=previous_diagnosis)
            symptoms.save()

            pharmacy_name = pharmacy_form.cleaned_data['pharmacy_name']
            pharmacy_address = pharmacy_form.cleaned_data['pharmacy_address']
            pharmacy_phone = pharmacy_form.cleaned_data['pharmacy_phone']

            pharmacy = Preferred_Pharmacy(patient=patient,
                                          pharmacy_name=pharmacy_name,
                                          pharmacy_address=pharmacy_address,
                                          pharmacy_phone=pharmacy_phone)
            pharmacy.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('easyconnect:video-chat', args=(patient_id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        symptom_form = SymptomsForm()
        pharmacy_form = PharmacyForm()


    context = {
        'symptom_form': symptom_form,
        'pharmacy_form': pharmacy_form,
        'zip': patient.zip
    }

    return render(request, 'EasyConnect/connect-2.html', context)


def video_chat(request, patient_id):
    context = {
        'patient_id': patient_id
    }

    return render(request, 'EasyConnect/VideoChat.html', context)


def provider_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    symptoms = get_object_or_404(Symptoms, pk=patient_id)
    video = get_object_or_404(Video_Chat, pk=patient_id)

    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        provider_form = ProviderForm(request.POST)
        if provider_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            hpi = provider_form.cleaned_data['hpi']
            #assessments = form.cleaned_data['assessments']
            treatment = provider_form.cleaned_data['treatment']
            followup = provider_form.cleaned_data['followup']
            return_to_work_notes = provider_form.cleaned_data['return_to_work_notes']

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
        provider_form = ProviderForm()

    context = {
        'provider_form': provider_form
    }

    return render(request, 'EasyConnect/provider-view.html', context)

