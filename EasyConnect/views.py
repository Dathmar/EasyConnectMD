import os
import csv
import json
import threading

from datetime import datetime

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.utils import timezone
from django.db import connection

from EasyConnect.forms import PatientForm, SymptomsForm, ProviderForm, PharmacyForm, PaymentForm, ICD10CodeLoad
from EasyConnect.models import Patient, Symptoms, ProviderNotes, Preferred_Pharmacy, Appointments, Payment, Icd10

from square.client import Client

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant

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

    off_hours = False
    # if not (8 <= timezone.localtime().hour < 20):
    #    off_hours = True

    context = {
        'form': form,
        'off_hours': off_hours
    }

    return render(request, 'EasyConnect/connect.html', context)


def connect_2(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    if Appointments.objects.filter(patient_id=patient.id):
        return HttpResponseRedirect(reverse('easyconnect:video-chat', args=(patient_id,)))

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
                payment_form = PaymentForm()
                payment_status = "Failed"
                payment_errors = []

                for error in result.errors:
                    if error['code'] == 'GENERIC_DECLINE':
                        payment_errors.append('Sorry but the card processing did not complete.  Please check your card'
                                              ' or try another payment method.')
                    elif error['code'] == 'CCV_ERROR':
                        payment_errors.append('The CCV did not match the card number.')
                    else:
                        payment_errors.append(error)

            payment = Payment(patient=patient,
                              nonce=nonce,
                              status=payment_status,
                              response=result.body)

            payment.save()

            if payment_status != 'Failed':
                if not Appointments.objects.filter(patient_id=patient.id):
                    appointment = Appointments(patient=patient,
                                               status='Ready for Provider',
                                               seen_by=None,
                                               last_update_user=None)
                    appointment.save()

                    # send e-mails
                    send_patient_notification(patient_id)
                    send_provider_notification(patient_id)

                return HttpResponseRedirect(reverse('easyconnect:video-chat', args=(patient_id,)))
    # If this is a GET (or any other method) create the default form.
    else:
        symptom_form = SymptomsForm()
        pharmacy_form = PharmacyForm()
        payment_form = PaymentForm()
        payment_errors = None

    context = {
        'symptom_form': symptom_form,
        'pharmacy_form': pharmacy_form,
        'payment_form': payment_form,
        'zip': patient.zip,
        'payment_errors': payment_errors
    }

    return render(request, 'EasyConnect/connect-2.html', context)


def video_chat(request, patient_id):
    patient = get_object_or_404(Patient, pk=patient_id)
    twilio_account_sid = settings.TWILIO_ACCOUNT_SID
    twilio_api_key_sid = settings.TWILIO_API_KEY_SID
    twilio_api_key_secret = settings.TWILIO_API_KEY_SECRET
    patient_name = f'{patient.first_name} {patient.last_name}'
    token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                        twilio_api_key_secret, identity=patient_name)
    token.add_grant(VideoGrant(room=str(patient_id)))

    context = {
        'patient_id': patient_id,
        'token': token.to_jwt().decode(),
        'username': patient_name
    }
    return render(request, 'EasyConnect/VideoChat.html', context)


def provider_dashboard(request):
    ready_appointments = get_appointments('Ready for Provider')
    completed_appointments = get_appointments('Appointment Complete', 10, 'DESC')
    active_appointments = get_appointments('Being seen by provider')

    context = {
        'ready_appointments': ready_appointments,
        'active_appointments': active_appointments,
        'completed_appointments': completed_appointments
    }

    return render(request, "EasyConnect/dashboard.html", context)


def provider_view(request, patient_id):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('easyconnect:dashboard'))

    patient = get_object_or_404(Patient, pk=patient_id)
    symptoms = get_object_or_404(Symptoms, patient_id=patient_id)
    preferred_pharmacy = get_object_or_404(Preferred_Pharmacy, patient_id=patient_id)
    appointment = Appointments.objects.filter(patient_id=patient_id).order_by('-create_datetime').first()

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

            # TODO need some edge case stuff here
            appointment.status = 'Appointment Complete'
            appointment.update_datetime = datetime.now()
            appointment.seen_by = request.user
            appointment.save(update_fields=['status', 'update_datetime', 'seen_by'])

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('easyconnect:dashboard'))

    # If this is a GET (or any other method) create the default form.
    else:
        # update appointment status
        # TODO need some edge case stuff here
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
                                      'providernotes__hpi', 'providernotes__followup', 'providernotes__treatment',
                                      'providernotes__id')\
        .order_by('-create_datetime')

    #providernote_ids = []
    #for patient_record in patient_records:
    #    providernote_ids.append(patient_record['providernotes__id'])

    #patient_assessments = get_patient_assessments(providernote_ids)

    twilio_account_sid = settings.TWILIO_ACCOUNT_SID
    twilio_api_key_sid = settings.TWILIO_API_KEY_SID
    twilio_api_key_secret = settings.TWILIO_API_KEY_SECRET
    provider_name = 'Provider'
    token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                        twilio_api_key_secret, identity=provider_name)
    token.add_grant(VideoGrant(room=str(patient_id)))

    context = {
        'provider_form': provider_form,
        'patient': patient,
        'patient_form': patient_form,
        'symptoms': symptoms,
        'symptoms_form': symptoms_form,
        'preferred_pharmacy_form': preferred_pharmacy_form,
        'patient_records': patient_records,
        'username': provider_name,
        'token': token.to_jwt().decode()
        #'patient_assessments': patient_assessments
    }

    return render(request, 'EasyConnect/provider-view.html', context)


def get_appointments(status, count=100, order_by='ASC'):
    sql = f'''SELECT 
                ecp.id as "patient_id",
                eca.status as "appointment_status",
                concat(au.first_name, ' ', au.last_name)  as "seen_by",
                concat(ecp.first_name, ' ', ecp.last_name) as "patient_name",
                ecp.dob as "patient_dob"
            FROM "EasyConnect_appointments" as eca
            LEFT JOIN "EasyConnect_patient" as ecp on eca.patient_id=ecp.id
            LEFT JOIN "auth_user" as au on eca.seen_by_id=au.id
            WHERE eca.status='{status}'
            ORDER BY eca.create_datetime {order_by}
            LIMIT {count}'''

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()

    if not result:
        return None

    return [dict(zip([key[0] for key in cursor.description], row)) for row in result]



def get_patient_assessments(provider_note_ids):
    patient_assessments = []
    if provider_note_ids:
        for provider_note_id in provider_note_ids:
            note_assessment = []
            if provider_note_id:
                sql = 'SELECT ' \
                      'icd10."ICD10_DSC" FROM public."EasyConnect_icd10" as icd10 where id in ' \
                      '(select ecpa."icd10_id" from public."EasyConnect_providernotes_assessments" ' \
                      f'as ecpa where ecpa."providernotes_id"={provider_note_id});'
                with connection.cursor() as cursor:
                    result = cursor.execute(sql)
                    if result:
                        for row in result:
                            note_assessment.append(row[0])

            patient_assessments.append(','.join(note_assessment))

    return patient_assessments


def get_object_data_or_set_defaults(to_get_object):
    return_obj = {}
    if to_get_object:
        return_obj['pk'] = to_get_object.pk
        return_obj['create_datetime'] = to_get_object.create_datetime
    else:
        return_obj['pk'] = None
        return_obj['create_datetime'] = None

    return return_obj


def icd10_load(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('easyconnect:dashboard'))

    if request.method == 'POST':
        form = ICD10CodeLoad(request.POST, request.FILES)
        if form.is_valid():
            csv_reader = csv.reader(request.FILES['file'].read().decode("utf-8").splitlines(), delimiter=',')
            Icd10.objects.all().delete()
            for row in csv_reader:
                icd10_row = Icd10(IDC10_CDE=row[1],
                                  ICD10_DSC=row[2])
                icd10_row.save()

            return HttpResponseRedirect(reverse('easyconnect:dashboard'))
    else:
        form = ICD10CodeLoad()
    return render(request, 'EasyConnect/load_icd10.html', {'form': form})


def login_request(request):
    return HttpResponseRedirect(reverse('easyconnect:login'))


def logout_request(request):
    logout(request)
    return HttpResponseRedirect(reverse('easyconnect:dashboard'))


def password_change(request):
    return HttpResponseRedirect(reverse('easyconnect:password-change'))


def send_provider_notification(patient_id):
    patient = Patient.objects.filter(pk=patient_id).first()
    body = f"""
            A new video chat has been received from: {patient.first_name} {patient.last_name}.
            
            Click the following link to initiate the 1-on-1 video chat:
            <a href='https://dev-connect.easyconnectmd.com/provider/{patient_id}'>https://dev-connect.easyconnectmd.com/provider/{patient_id}</a>
            
            Patient Info
            Name: {patient.first_name} {patient.last_name}
            Phone: {patient.phone_number}
            Email: {patient.email}
            """

    html_body = f"""
            <!DOCTYPE html>
            <html>
                <head>
                </head>
                <body>
                    <p>A new video chat has been received from: {patient.first_name} {patient.last_name}.</p>
                    <p></p>
                    <p>Click the following link to initiate the 1-on-1 video chat:</p>
                    <p><a href='https://dev-connect.easyconnectmd.com/provider/{patient_id}'>https://dev-connect.easyconnectmd.com/provider/{patient_id}</a></p>
                    <p></p>
                    <p>Patient Info</p>
                    <p>Name: {patient.first_name} {patient.last_name}</p>
                    <p>Phone: {patient.phone_number}</p>
                    <p>Email: {patient.email}</p>
                </body>
            </html>
            """

    EmailThread(
        subject=f'Video Chat for {patient.first_name} {patient.last_name}',
        message=body,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=['gfarias@easyconnectmd.net', 'acortez@easyconnectmd.net', 'adanner@easyconnectmd.net'],
        fail_silently=False,
        html_message=html_body
    ).start()


def send_patient_notification(patient_id):
    patient = Patient.objects.filter(pk=patient_id).first()
    payment_info = Payment.objects.filter(patient_id=patient_id, status='Paid').values('response').first()['response']
    payment_info = json.loads(payment_info.replace("\'", "\""))

    payment_date = payment_info['payment']['created_at']
    payment_card_type = payment_info['payment']['card_details']['card']['card_brand']
    payment_card_last4 = payment_info['payment']['card_details']['card']['last_4']
    payment_amount = payment_info['payment']['amount_money']['amount'] / 100

    body = f"""
        Hi {patient.first_name},

        If you get disconnected from your online appointment, please click the following link to re-join:

        <a href='https://dev-connect.easyconnectmd.com/video-chat/{patient_id}'>Click to Rejoin</a>

        Thank you for choosing EasyConnectMD!

        Need technical support?
        You can email us at <a href='mailto:info@easyconnectmd.net'>info@easyconnectmd.net</a>

        === Receipt Information ===
        Date: {payment_date}
        Total paid: ${payment_amount}
        {payment_card_type} ending in {payment_card_last4}
        """

    html_body = f"""
        <!DOCTYPE html>
        <html>
            <head>
            </head>
            <body>
                <p>Hi {patient.first_name},</p>
                <p></p>
                <p>If you get disconnected from your online appointment, please click the following link to re-join:</p>
                <p></p>
                <p><a href='https://dev-connect.easyconnectmd.com/video-chat/{patient_id}'>Click to Rejoin</a></p>
                <p></p>
                <p>Thank you for choosing EasyConnectMD!</p>
                <p></p>
                <p>Need technical support?</p>
                <p>You can email us at <a href='mailto:info@easyconnectmd.net'>info@easyconnectmd.net</a></p>
                <p></p>
                <p>=== Receipt Information ===</p>
                <p>Date: {payment_date}</p>
                <p>Total paid: ${payment_amount}</p>
                <p>{payment_card_type} ending in {payment_card_last4}</p>
            </body>
        </html>
        """

    EmailThread(
        subject='In case you get disconnected',
        message=body,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[patient.email],
        fail_silently=False,
        html_message=html_body
    ).start()


class EmailThread(threading.Thread):
    def __init__(self, subject, message, recipient_list, from_email, fail_silently, html_message):
        self.subject = subject
        self.recipient_list = recipient_list
        self.message = message
        self.from_email = from_email
        self.fail_silently = fail_silently
        self.html_message = html_message
        threading.Thread.__init__(self)

    def run(self):
        msg = send_mail(subject=self.subject, message=self.message, from_email=self.from_email,
                        recipient_list=self.recipient_list, fail_silently=self.fail_silently,
                        html_message=self.html_message)
