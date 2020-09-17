import os
import csv
import json
import threading

from datetime import datetime
from pytz import timezone
import pytz

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.db import connection

from EasyConnect.forms import PatientForm, SymptomsForm, ProviderForm, PharmacyForm, PaymentForm, ICD10CodeLoad, \
    AffiliateForm
from EasyConnect.models import Patient, Symptoms, ProviderNotes, Preferred_Pharmacy, Appointments, Payment, Icd10, \
    Affiliate

from square.client import Client

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from twilio.rest import Client as twilio_client

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_affiliate_context(affiliate_url):
    affiliate = None
    if affiliate_url:
        affiliate = Affiliate.objects.filter(affiliate_url=affiliate_url).first()

    if not affiliate:
        affiliate = Affiliate.objects.filter(affiliate_name='EasyConnect').first()

    context = {
        'affiliate': affiliate,
    }

    return context


def get_affiliate_object(affiliate_url):
    if affiliate_url:
        affiliate = Affiliate.objects.filter(affiliate_url=affiliate_url).first()
        if affiliate:
            return affiliate

    return Affiliate.objects.filter(affiliate_name='EasyConnect').first()


# Create your views here.
def index(request):
    return index_affiliate(request, '')


def index_affiliate(request, affiliate_url):
    affiliate_url = affiliate_url.lower()
    context = get_affiliate_context(affiliate_url)
    return render(request, 'EasyConnect/index.html', context)


def our_story(request):
    return our_story_affiliate(request, '')


def our_story_affiliate(request, affiliate_url):
    affiliate_url = affiliate_url.lower()
    context = get_affiliate_context(affiliate_url)
    return render(request, 'EasyConnect/our-story.html', context)


def faq(request):
    return faq_affiliate(request, '')


def faq_affiliate(request, affiliate_url):
    affiliate_url = affiliate_url.lower()
    context = get_affiliate_context(affiliate_url)
    return render(request, 'EasyConnect/faq.html', context)


def privacy_policy(request):
    return faq_affiliate(request, '')


def privacy_policy_affiliate(request, affiliate_url):
    affiliate_url = affiliate_url.lower()
    context = get_affiliate_context(affiliate_url)
    return render(request, 'EasyConnect/privacy-policy.html', context)


def connect(request):
    return connect_affiliate(request, '')


def connect_affiliate(request, affiliate_url):
    affiliate_url = affiliate_url.lower()
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
            affiliate = get_affiliate_object(affiliate_url=affiliate_url)
            patient = Patient(first_name=first_name,
                              last_name=last_name,
                              phone_number=phone_number,
                              email=email,
                              dob=dob,
                              gender=gender,
                              zip=zip,
                              tos=tos,
                              affiliate=affiliate)
            patient.save()

            # redirect to a new URL:
            if affiliate_url:
                return HttpResponseRedirect(reverse('easyconnect:connect-2-affiliate',
                                                    kwargs={'patient_id': patient.id,
                                                            'affiliate_url': affiliate_url}))
            else:
                return HttpResponseRedirect(reverse('easyconnect:connect-2', args=(patient.id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        form = PatientForm()

    server_time = datetime.now(pytz.utc)

    tz = timezone(settings.DISPLAY_TZ)
    loc_dt = server_time.astimezone(tz)
    off_hours = False
    if not (8 <= loc_dt.hour < 20):
        off_hours = True

    affiliate = get_affiliate_context(affiliate_url=affiliate_url)

    context = {
        'form': form,
        'off_hours': off_hours,
    }
    context.update(affiliate)
    return render(request, 'EasyConnect/connect.html', context)


def connect_timeless(request):
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
            affiliate = get_affiliate_object(affiliate_url='')

            patient = Patient(first_name=first_name,
                              last_name=last_name,
                              phone_number=phone_number,
                              email=email,
                              dob=dob,
                              gender=gender,
                              zip=zip,
                              tos=tos,
                              affiliate=affiliate)
            patient.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('easyconnect:connect-2', args=(patient.id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        form = PatientForm()

    off_hours = False

    context = {
        'form': form,
        'off_hours': off_hours
    }

    return render(request, 'EasyConnect/connect.html', context)


def connect_2(request, patient_id):
    return connect_2_affiliate(request, patient_id, '')


def connect_2_affiliate(request, patient_id, affiliate_url):
    affiliate_url = affiliate_url.lower()
    patient = get_object_or_404(Patient, pk=patient_id)
    payment_errors = None
    if Appointments.objects.filter(patient_id=patient.id):
        if affiliate_url:
            return HttpResponseRedirect(reverse('easyconnect:video-chat', kwargs={'patient_id': patient.id,
                                                                                  'affiliate_url': affiliate_url}))
        else:
            return HttpResponseRedirect(reverse('easyconnect:video-chat', args=(patient_id,)))

    affiliate = get_affiliate_object(affiliate_url=affiliate_url)

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
            previous_payments = Payment.objects.filter(patient_id=patient_id).count()

            # process the payment
            body = {
                'source_id': nonce,
                'idempotency_key': str(patient_id) + '-' + str(previous_payments),
                'amount_money': {
                    'amount': int(affiliate.affiliate_price),
                    'currency': 'USD'
                }
            }

            client = Client(
                access_token=settings.SQUARE_ACCESS_TOKEN,
                environment=settings.SQUARE_ENVIRONMENT,
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
                if affiliate_url:
                    return HttpResponseRedirect(reverse('easyconnect:video-chat-affiliate',
                                                        kwargs={'patient_id': patient.id,
                                                                'affiliate_url': affiliate_url}))
                else:
                    return HttpResponseRedirect(reverse('easyconnect:video-chat', args=(patient_id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        symptom_form = SymptomsForm()
        pharmacy_form = PharmacyForm()
        payment_form = PaymentForm()

    affiliate = get_affiliate_context(affiliate_url=affiliate_url)

    context = {
        'symptom_form': symptom_form,
        'pharmacy_form': pharmacy_form,
        'payment_form': payment_form,
        'zip': patient.zip,
        'payment_errors': payment_errors,
        'square_js_url': settings.SQUARE_JS_URL,
    }
    context.update(affiliate)
    return render(request, 'EasyConnect/connect-2.html', context)


def video_chat(request, patient_id):
    return video_chat_affiliate(request, patient_id, '')


def video_chat_affiliate(request, patient_id, affiliate_url):
    affiliate_url = affiliate_url.lower()
    patient = get_object_or_404(Patient, pk=patient_id)
    patient_name = f'{patient.first_name} {patient.last_name}'

    affiliate = get_affiliate_context(affiliate_url=affiliate_url)

    context = {
        'username': patient_name,
        'patient_id': str(patient_id),
    }
    context.update(affiliate)
    return render(request, 'EasyConnect/VideoChat.html', context)


def lucky_provider(request):
    ready_appointments = get_appointments('Ready for Provider')

    if ready_appointments:
        patient_id = ready_appointments[0]['patient_id']
        patient_name = ready_appointments[0]['patient_name']

        return provider_view(request, patient_id)
    else:
        return provider_dashboard(request)


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

            # TODO need some edge case stuff here for when a provider is already seeing a patient
            appointment.status = 'Appointment Complete'
            appointment.update_datetime = datetime.now()
            appointment.seen_by = request.user
            appointment.save(update_fields=['status', 'update_datetime', 'seen_by'])

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('easyconnect:dashboard'))

    # If this is a GET (or any other method) create the default form.
    else:
        # update appointment status
        # TODO need some edge case stuff here for when a provider is already seeing a patient
        if appointment.status != 'Appointment Complete' and not appointment.seen_by:
            appointment.status = 'Being seen by provider'
            appointment.seen_by = request.user
            appointment.save(update_fields=['status', 'seen_by'])

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

        tz = timezone(settings.DISPLAY_TZ)
        today = tz.localize(datetime.today())
        patient_age = today.year - patient.dob.year - ((today.month, today.day) < (patient.dob.month, patient.dob.day))
        provider_notes = ProviderNotes.objects.filter(patient_id=patient_id).first()

        if provider_notes:
            provider_form = ProviderForm(initial={'hpi': provider_notes.hpi,
                                                  'treatment': provider_notes.treatment,
                                                  'followup': provider_notes.followup,
                                                  'assessments': provider_notes.assessments.all(),
                                                  'return_to_work_notes': provider_notes.return_to_work_notes})
        else:
            provider_form = ProviderForm()

    patient_records = get_patient_records(patient_id)


    provider_name = 'Provider'
    context = {
        'provider_form': provider_form,
        'patient': patient,
        'patient_form': patient_form,
        'symptoms': symptoms,
        'symptoms_form': symptoms_form,
        'preferred_pharmacy_form': preferred_pharmacy_form,
        'patient_records': patient_records,
        'username': provider_name,
        'patient_age': patient_age
    }

    return render(request, 'EasyConnect/provider-view.html', context)


def video_token(request):
    if request.method == 'POST':
        patient_id = json.loads(request.body)['patient_id']
        identity = json.loads(request.body)['username']

        twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        twilio_api_key_sid = settings.TWILIO_API_KEY_SID
        twilio_api_key_secret = settings.TWILIO_API_KEY_SECRET
        # twilio_auth_token = settings.TWILIO_AUTH_TOKEN

        # client = twilio_client(twilio_account_sid, twilio_auth_token)
        # rooms = client.video.rooms.list(unique_name=patient_id, limit=20)

        token = AccessToken(twilio_account_sid, twilio_api_key_sid,
                            twilio_api_key_secret, identity=identity)

        '''if not rooms:
            client.video.rooms.create(
                record_participants_on_connect=False,
                type='group-small',
                unique_name=patient_id
            )'''

        token.add_grant(VideoGrant(room=patient_id))

        data = {'token': token.to_jwt().decode()}
        data = json.dumps(data)
        return HttpResponse(data, status=200, content_type='application/json')

    return HttpResponse(None, status=401)


def server_time(request):
    server_time = datetime.now(pytz.utc)

    tz = timezone(settings.DISPLAY_TZ)
    loc_dt = server_time.astimezone(tz)
    off_hours = False
    if not (8 <= loc_dt.hour < 20):
        off_hours = True

    context = {
        'local_time': datetime.strftime(loc_dt, '%m/%d/%Y %H:%M'),
        'server_time': datetime.strftime(server_time, '%m/%d/%Y %H:%M'),
        'local_hour': datetime.strftime(loc_dt, '%H'),
        'off_hours': off_hours
    }
    return render(request, 'EasyConnect/server-time.html', context)


def get_patient_records(patient_id):
    sql = f'''
            with PNA as ( 
                select STRING_AGG(icd."ICD10_DSC"::character varying, ', ') icd10_dsc, ecpa.providernotes_id from 
                    public."EasyConnect_providernotes_assessments" ecpa
                inner join public."EasyConnect_icd10" icd on ecpa."icd10_id"=icd.id
                group by ecpa.providernotes_id
            ),
            PNMax as (
            SELECT 
                max(PN2.create_datetime) AS mxdate, PN2.patient_id
            FROM public."EasyConnect_providernotes" AS PN2
            GROUP BY PN2.patient_id
            ),
            patient as (
            SELECT
                pat.id, concat(pat.first_name, ' ', pat.last_name) patient_name, pat.dob
            FROM public."EasyConnect_patient" pat
            ) 
            SELECT
                PNMax.mxdate as create_datetime, 
                sym.symptom_description symptom_description, sym.allergies allergies, 
                sym.medications medications, sym.previous_diagnosis previous_diagnosis, PN.hpi hpi, 
                PNA.icd10_dsc icd10_dsc, PN.treatment treatment, PN.followup, 
                concat(au.first_name, ' ', last_name) seen_by, patient.patient_name, patient.dob
            FROM public."EasyConnect_providernotes" AS PN
                INNER JOIN PNMax ON PN.patient_id=PNMax.patient_id AND PN.create_datetime=PNMax.mxdate
                INNER JOIN PNA ON PN.id=PNA.providernotes_id
                INNER JOIN public."EasyConnect_symptoms" sym ON PN.patient_id=sym.patient_id
                INNER JOIN public."EasyConnect_appointments" eca ON PN.patient_id=eca.patient_id
                INNER JOIN patient ON patient.id=eca.patient_id
                LEFT JOIN "auth_user" as au on eca.seen_by_id=au.id
            WHERE PN.patient_id!='{patient_id}' and patient.patient_name=(select pat.patient_name from patient pat where
                pat.id='{patient_id}') and patient.dob=(select pat.dob from patient pat where
                pat.id='{patient_id}')
            ORDER BY create_datetime DESC
        '''

    with connection.cursor() as cursor:
        cursor.execute(sql)
        result = cursor.fetchall()

    if not result:
        return None

    return [dict(zip([key[0] for key in cursor.description], row)) for row in result]

def get_appointments(status, count=100, order_by='ASC'):
    sql = f'''SELECT 
                ecp.id as "patient_id",
                eca.status as "appointment_status",
                concat(au.first_name, ' ', au.last_name)  as "seen_by",
                concat(ecp.first_name, ' ', ecp.last_name) as "patient_name",
                ecp.dob as "patient_dob",
                eca.create_datetime as "created_at"
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

    context = {'form': form}
    return render(request, 'EasyConnect/load_icd10.html', context)


def affiliate_load(request):
    if request.method == 'POST':
        form = AffiliateForm(request.POST)
        if form.is_valid():
            affiliate_name = form.cleaned_data['affiliate_name']
            affiliate_logo = form.cleaned_data['affiliate_logo']
            affiliate_url = form.cleaned_data['affiliate_url']
            affiliate_price = form.cleaned_data['affiliate_price']

            affiliate = Affiliate(affiliate_name=affiliate_name,
                                  affiliate_logo=affiliate_logo,
                                  affiliate_url=affiliate_url,
                                  affiliate_price=affiliate_price)

            affiliate.save()
            return HttpResponseRedirect(reverse('easyconnect:dashboard'))
    else:
        form = AffiliateForm()

    context = {'form': form}
    return render(request, 'EasyConnect/load_affiliate.html', context)


def login_request(request):
    return HttpResponseRedirect(reverse('easyconnect:login'))


def logout_request(request):
    logout(request)
    return HttpResponseRedirect(reverse('easyconnect:dashboard'))


def send_provider_notification(patient_id):
    patient = Patient.objects.filter(pk=patient_id).first()
    body = f"""
            A new video chat has been received from: {patient.first_name} {patient.last_name}.
            
            Click the following link to initiate the 1-on-1 video chat:
            <a href='{settings.EMAIL_BASE_URL}/provider/{patient_id}'>{settings.EMAIL_BASE_URL}/provider/{patient_id}</a>
            
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
                    <p><a href='{settings.EMAIL_BASE_URL}/provider/{patient_id}'>{settings.EMAIL_BASE_URL}/provider/{patient_id}</a></p>
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
        recipient_list=settings.APPOINTMENT_RECIPIENT_LIST,
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

        <a href='{settings.EMAIL_BASE_URL}/video-chat/{patient_id}'>Click to Rejoin</a>

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
                <p><a href='{settings.EMAIL_BASE_URL}/video-chat/{patient_id}'>Click to Rejoin</a></p>
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
