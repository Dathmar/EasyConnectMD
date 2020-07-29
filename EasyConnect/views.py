import os

from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import logout
from django.contrib.auth.forms import AuthenticationForm

from EasyConnect.forms import PatientForm, SymptomsForm, ProviderForm, PharmacyForm, PaymentForm
from EasyConnect.models import Patient, Symptoms, ProviderNotes, Preferred_Pharmacy, Appointments, Payment
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
        payment_form = PaymentForm(request.POST)

        if symptom_form.is_valid() and pharmacy_form.is_valid() and payment_form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            symptom_description = symptom_form.cleaned_data['symptom_description']
            allergies = symptom_form.cleaned_data['allergies']
            medications = symptom_form.cleaned_data['medications']
            previous_diagnosis = symptom_form.cleaned_data['previous_diagnosis']

            # get existing object if it exists and update.
            symptom_obj = get_object_data_or_set_defaults(Symptoms.objects.filter(patient_id=patient_id).first())

            symptoms = Symptoms(pk=symptom_obj['pk'],
                                patient=patient,
                                symptom_description=symptom_description,
                                allergies=allergies,
                                medications=medications,
                                previous_diagnosis=previous_diagnosis,
                                create_datetime=symptom_obj['create_datetime'],
                                update_datetime=datetime.now())
            symptoms.save()

            pharmacy_name = pharmacy_form.cleaned_data['pharmacy_name']
            pharmacy_address = pharmacy_form.cleaned_data['pharmacy_address']
            pharmacy_phone = pharmacy_form.cleaned_data['pharmacy_phone']

            # get existing object if it exists and update.
            pharmacy_obj = get_object_data_or_set_defaults(
                Preferred_Pharmacy.objects.filter(patient_id=patient_id).first())

            pharmacy = Preferred_Pharmacy(id=pharmacy_obj['pk'],
                                          patient=patient,
                                          pharmacy_name=pharmacy_name,
                                          pharmacy_address=pharmacy_address,
                                          pharmacy_phone=pharmacy_phone,
                                          create_datetime=pharmacy_obj['create_datetime'],
                                          update_datetime=datetime.now())
            pharmacy.save()

            # each payment attempt will generate a new nonce
            nonce = payment_form.cleaned_data['nonce']

            # process the payment
            body = {
                'source_id': nonce,
                'idempotency_key': str(patient_id),
                'amount_money': {
                    'amount': 3995,
                    'currency': 'USD'
                }
            }

            client = Client(
                access_token=settings.SQUARE_ACCESS_TOKEN,
                environment='sandbox',
            )

            payments_api = client.payments
            result = payments_api.create_payment(body)
            if result.is_success():
                payment_status = "Paid"
            elif result.is_error():
                payment_status = "Failed"

            payment = Payment(patient=patient,
                              nonce=nonce,
                              status=payment_status,
                              response=result)

            payment.save()

            if payment_status != 'Failed':
                appointment = Appointments(patient=patient,
                                           status='Ready for Provider',
                                           seen_by=None,
                                           last_update_user=None)
                appointment.save()
                return HttpResponseRedirect(reverse('easyconnect:video-chat', args=(patient_id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        symptom_form = SymptomsForm()
        pharmacy_form = PharmacyForm()
        payment_form = PaymentForm()

    context = {
        'symptom_form': symptom_form,
        'pharmacy_form': pharmacy_form,
        'payment_form': payment_form,
        'zip': patient.zip
    }

    return render(request, 'EasyConnect/connect-2.html', context)


def video_chat(request, patient_id):
    context = {
        'patient_id': patient_id
    }
    return render(request, 'EasyConnect/VideoChat.html', context)


def provider_dashboard(request):
    ready_appointments = Patient.objects.values('id', 'create_datetime', 'first_name', 'last_name', 'dob',
                                                'appointments__status').\
        filter(appointments__status='Ready for Provider').order_by('-create_datetime')
    completed_appointments = Patient.objects.values('id', 'first_name', 'last_name', 'dob', 'appointments__status',
                                                'appointments__seen_by').\
        filter(appointments__status='Appointment Complete')[:10]
    active_appointments = Patient.objects.values('id', 'first_name', 'last_name', 'dob', 'appointments__status',
                                                    'appointments__seen_by'). \
        filter(appointments__status='Being seen by provider')

    context = {
        'ready_appointments': ready_appointments,
        'active_appointments': active_appointments,
        'completed_appointments': completed_appointments
    }

    return render(request, "EasyConnect/dashboard.html", context)


def provider_view(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    symptoms = get_object_or_404(Symptoms, patient_id=patient_id)
    preferred_pharmacy = get_object_or_404(Preferred_Pharmacy, patient_id=patient_id)
    appointment = get_object_or_404(Appointments, patient_id=patient_id)

    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        provider_form = ProviderForm(request.POST)
        patient_form = PatientForm(request.POST)
        symptoms_form = SymptomsForm(request.POST)
        preferred_pharmacy_form = PharmacyForm(request.POST)
        if provider_form.is_valid():
            hpi = provider_form.cleaned_data['hpi']
            assessments = provider_form.cleaned_data['assessments']
            treatment = provider_form.cleaned_data['treatment']
            followup = provider_form.cleaned_data['followup']
            return_to_work_notes = provider_form.cleaned_data['return_to_work_notes']

            provider_notes = ProviderNotes(patient=patient,
                                           hpi=hpi,
                                           treatment=treatment,
                                           followup=followup,
                                           return_to_work_notes=return_to_work_notes)
            provider_notes.save()
            provider_notes.assessments.set(assessments)



            # TODO need some edge case stuff here for if the
            appointment.status = 'Appointment Complete'
            appointment.update_datetime = datetime.now()
            appointment.seen_by = request.user
            appointment.save(update_fields=['status', 'update_datetime', 'seen_by'])

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('easyconnect:dashboard'))

    # If this is a GET (or any other method) create the default form.
    else:
        # update appointment status
        # TODO need some edge case stuff here for if the
        if appointment.status != 'Appointment Complete':
            appointment.status = 'Being seen by provider'
            appointment.save(update_fields=['status'])

        preferred_pharmacy_form = PharmacyForm(initial={'pharmacy_phone': preferred_pharmacy.pharmacy_phone,
                                                        'pharmacy_address': preferred_pharmacy.pharmacy_address,
                                                        'pharmacy_name': preferred_pharmacy.pharmacy_name})
        patient_form = PatientForm(initial={'first_name': patient.first_name,
                                            'last_name': patient.last_name,
                                            'phone_number': patient.phone_number,
                                            'email': patient.email,
                                            'dob': patient.dob,
                                            'gender': patient.gender,
                                            'zip': patient.zip})
        symptoms_form = SymptomsForm(initial={'symptom_description': symptoms.symptom_description,
                                              'allergies': symptoms.allergies,
                                              'medications': symptoms.medications,
                                              'previous_diagnosis': symptoms.previous_diagnosis})

        provider_notes = ProviderNotes.objects.filter(patient_id=patient_id).first()

        if provider_notes:
            provider_form = ProviderForm(initial={'hpi': provider_notes.hpi,
                                                  'treatment': provider_notes.treatment,
                                                  'followup': provider_notes.followup,
                                                  'assessments': provider_notes.assessments.all(),
                                                  'return_to_work_notes': provider_notes.return_to_work_notes})
        else:
            provider_form = ProviderForm()

    patient_records = Patient.objects.filter(first_name=patient.first_name,
                                             last_name=patient.last_name,
                                             dob=patient.dob).\
        exclude(pk=patient_id).values('id', 'create_datetime', 'symptoms__allergies', 'symptoms__medications',
                                      'symptoms__previous_diagnosis', 'symptoms__symptom_description',
                                      'providernotes__hpi', 'providernotes__followup', 'providernotes__treatment')\
        .order_by('-create_datetime')

    #patient_assessments = Patient.objects.filter(first_name=patient.first_name,
    #                                         last_name=patient.last_name,
    #                                         dob=patient.dob). \
    #    exclude(pk=patient_id).values('id', 'providernotes__assessments__ICD10_DSC')

    #print(patient_assessments)


    context = {
        'provider_form': provider_form,
        'patient': patient,
        'patient_form': patient_form,
        'symptoms': symptoms,
        'symptoms_form': symptoms_form,
        'preferred_pharmacy_form': preferred_pharmacy_form,
        'patient_records': patient_records,
        #'patient_assessments': patient_assessments
    }

    return render(request, 'EasyConnect/provider-view.html', context)


def get_object_data_or_set_defaults(to_get_object):
    return_obj = {}
    if to_get_object:
        return_obj['pk'] = to_get_object.pk
        return_obj['create_datetime'] = to_get_object.create_datetime
    else:
        return_obj['pk'] = None
        return_obj['create_datetime'] = None

    return return_obj


def login_request(request):
    return HttpResponseRedirect(reverse('easyconnect:login'))


def logout_request(request):
    logout(request)
    return HttpResponseRedirect(reverse('easyconnect:dashboard'))


def password_change(request):
    return HttpResponseRedirect(reverse('easyconnect:password-change'))

