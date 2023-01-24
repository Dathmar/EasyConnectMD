import os
import csv
import json
import threading
import uuid

from datetime import datetime, timedelta
from django.utils import timezone
import pytz

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse, JsonResponse, HttpResponseNotAllowed
from django.urls import reverse
from django.conf import settings
from django.contrib.auth import logout
from django.core.mail import send_mail
from django.db import connection
from django.contrib.auth.models import User

from EasyConnect.forms import PatientForm, SymptomsForm, ProviderForm, PaymentForm, ICD10CodeLoad, \
    AffiliateForm, CouponForm, VitalsForm
from EasyConnect.models import Patient, Symptoms, ProviderNotes, Appointments, Payment, Icd10, \
    Affiliate, Coupon, Patient_Cost, Vitals

from square.client import Client

from twilio.jwt.access_token import AccessToken
from twilio.jwt.access_token.grants import VideoGrant
from twilio.rest import Client as TwilioRestClient

import logging

logger = logging.getLogger('app_api')

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def get_affiliate_context(affiliate_url):
    affiliate = None
    if affiliate_url != '':
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


def splash_page(request):
    return splash_page_affiliate(request, '')


def splash_page_affiliate(request, affiliate_url):
    affiliate_url = affiliate_url.lower()
    context = get_affiliate_context(affiliate_url)
    return render(request, 'EasyConnect/splash-page.html', context)


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

            patient_cost = Patient_Cost(patient_id=patient.id, cost=affiliate.affiliate_price)
            patient_cost.save()

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

    off_hours = is_offhours()

    affiliate = get_affiliate_context(affiliate_url=affiliate_url)

    context = {
        'form': form,
        'off_hours': off_hours,
        'is_holiday': is_holiday(),
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

            patient_cost = Patient_Cost(patient_id=patient.id, cost=affiliate.affiliate_price)
            patient_cost.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('easyconnect:connect-2', args=(patient.id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        form = PatientForm()

    off_hours = False

    affiliate = get_affiliate_context(affiliate_url='')
    context = {
        'form': form,
        'off_hours': off_hours
    }
    context.update(affiliate)
    return render(request, 'EasyConnect/connect.html', context)


def connect_2(request, patient_id):
    return connect_2_affiliate(request, patient_id, '')


def connect_2_affiliate(request, patient_id, affiliate_url):
    affiliate_url = affiliate_url.lower()
    patient = get_object_or_404(Patient, pk=patient_id)
    patient_cost = Patient_Cost.objects.filter(patient=patient_id).first()
    affiliate_obj = get_affiliate_object(affiliate_url=affiliate_url)

    if not patient_cost:
        logger.info(f'{patient.id} Adding patient cost.')
        patient_cost = Patient_Cost(patient_id=patient.id, cost=affiliate_obj.affiliate_price)
        patient_cost.save()

    payment_errors = None

    # TODO add handling for completed appointments.
    if Appointments.objects.filter(patient_id=patient.id):
        if affiliate_url:
            return HttpResponseRedirect(reverse('easyconnect:video-chat-affiliate',
                                                kwargs={'patient_id': patient.id,
                                                        'affiliate_url': affiliate_url}))
        else:
            return HttpResponseRedirect(reverse('easyconnect:video-chat', args=(patient_id,)))

    if request.method == 'POST':
        logger.info(f'{patient.id} patient submitting payment')
        # Create a form instance and populate it with data from the request (binding):
        symptom_form = SymptomsForm(request.POST)
        payment_form = PaymentForm(request.POST)
        coupon_form = CouponForm(request.POST)
        vitals_form = VitalsForm(request.POST)

        if symptom_form.is_valid() and vitals_form.is_valid() and (payment_form.is_valid() or patient_cost <= 0):
            logger.info(f'{patient.id} forms are valid')

            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            pancreatitis_thyroid_cancer = symptom_form.cleaned_data['pancreatitis_thyroid_cancer']
            allergies = symptom_form.cleaned_data['allergies']
            medications = symptom_form.cleaned_data['medications']
            previous_diagnosis = symptom_form.cleaned_data['previous_diagnosis']

            # get existing object if it exists and update.
            symptom_obj = get_object_data_or_set_defaults(Symptoms.objects.filter(patient_id=patient_id).first())

            height_feet = vitals_form.cleaned_data['height_feet']
            height_inches = vitals_form.cleaned_data['height_inches']
            weight = vitals_form.cleaned_data['weight']

            vitals = Vitals(
                patient=patient,
                height_feet=height_feet,
                height_inches=height_inches,
                weight=weight
            )
            vitals.save()

            symptoms = Symptoms(pk=symptom_obj['pk'],
                                patient=patient,
                                pancreatitis_thyroid_cancer=pancreatitis_thyroid_cancer,
                                allergies=allergies,
                                medications=medications,
                                previous_diagnosis=previous_diagnosis,
                                create_datetime=symptom_obj['create_datetime'],
                                update_datetime=datetime.now())
            symptoms.save()

            # only generate payment if patient cost is greater than 0
            if int(patient_cost.cost) > 0:
                logger.info(f'{patient.id} processing payment.')
                # each payment attempt will generate a new nonce
                nonce = request.session.get('nonce')
                idempotency_key = request.session.get('idempotency_key')

                logger.info(f'{patient.id} nonce {nonce} idempotency_key {idempotency_key}')

                # process the payment
                body = {
                    'source_id': nonce,
                    'idempotency_key': idempotency_key,
                    'amount_money': {
                        'amount': int(patient_cost.cost),
                        'currency': 'USD'
                    }
                }

                client = Client(
                    access_token=settings.SQUARE_ACCESS_TOKEN,
                    environment=settings.SQUARE_ENVIRONMENT,
                )

                payments_api = client.payments
                result = payments_api.create_payment(body)
                payment_status = ""
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
            else:
                payment_status = "NA"

            request.session['idempotency_key'] = False
            request.session['nonce'] = False

            if payment_status != 'Failed':
                # add 1 to the coupon uses.
                coupon = patient_cost.coupon
                if coupon:
                    coupon.current_uses += 1

                    coupon.update_datetime = datetime.now()
                    coupon.save(update_fields=['current_uses', 'update_datetime'])

                if not Appointments.objects.filter(patient_id=patient.id):
                    appointment = Appointments(patient=patient,
                                               status='Ready for Provider',
                                               seen_by=None,
                                               last_update_user=None)
                    appointment.save()

                    # send e-mails
                    # send_patient_notification(patient_id)
                    # send_provider_notification(patient_id)
                if affiliate_url:
                    return HttpResponseRedirect(reverse('easyconnect:video-chat-affiliate',
                                                        kwargs={'patient_id': patient.id,
                                                                'affiliate_url': affiliate_url}))
                else:
                    return HttpResponseRedirect(reverse('easyconnect:video-chat', args=(patient_id,)))

    # If this is a GET (or any other method) create the default form.
    else:
        symptom_form = SymptomsForm()
        payment_form = PaymentForm()
        coupon_form = CouponForm()
        vitals_form = VitalsForm()

    if not request.session.get('idempotency_key'):
        request.session['idempotency_key'] = str(uuid.uuid4())
        request.session['nonce'] = False

    affiliate = get_affiliate_context(affiliate_url=affiliate_url)

    context = {
        'vitals_form': vitals_form,
        'symptom_form': symptom_form,
        'payment_form': payment_form,
        'coupon_form': coupon_form,
        'patient_id': patient_id,
        'patient_cost': patient_cost,
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


def call_stats(request):
    today = datetime.now()

    first_form = Patient.objects.filter(create_datetime__range=(today-timedelta(days=7), today))
    appointments = Appointments.objects.filter(create_datetime__range=(today-timedelta(days=7), today))
    affiliates = Affiliate.objects.all()

    first_by_affiliates = {}
    appointments_by_affiliates = {}

    for affiliate in affiliates:
        first_by_affiliates.update({affiliate: first_form.filter(affiliate=affiliate).count()})
        appointments_by_affiliates.update({affiliate: appointments.filter(patient__affiliate=affiliate).count()})

    context = {
        'first_form': first_form,
        'appointments': appointments,
        'first_by_affiliates': first_by_affiliates,
        'appointments_by_affiliates': appointments_by_affiliates,
    }

    return render(request, "EasyConnect/stats.html", context)


def provider_view(request, patient_id):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('easyconnect:dashboard'))

    patient = get_object_or_404(Patient, pk=patient_id)
    symptoms = get_object_or_404(Symptoms, patient_id=patient_id)

    appointment = Appointments.objects.filter(patient_id=patient_id).order_by('-create_datetime').first()

    if request.method == 'POST':
        # Create a form instance and populate it with data from the request (binding):
        provider_form = ProviderForm(request.POST)
        patient_form = PatientForm(request.POST)
        symptoms_form = SymptomsForm(request.POST)

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

        patient_form = PatientForm(initial={'first_name': patient.first_name,
                                            'last_name': patient.last_name,
                                            'phone_number': patient.phone_number,
                                            'email': patient.email,
                                            'dob': patient.dob,
                                            'gender': patient.gender,
                                            'zip': patient.zip})
        symptoms_form = SymptomsForm(initial={'pancreatitis_thyroid_cancer': symptoms.pancreatitis_thyroid_cancer,
                                              'allergies': symptoms.allergies,
                                              'medications': symptoms.medications,
                                              'previous_diagnosis': symptoms.previous_diagnosis})


        today = datetime.today()
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

        data = {'token': token.to_jwt()}
        data = json.dumps(data)
        return HttpResponse(data, status=200, content_type='application/json')

    return HttpResponse(None, status=401)


def provider_in_chat(request):
    if request.method == 'POST':
        patient_id = json.loads(request.body)['patient_id']

        twilio_account_sid = settings.TWILIO_ACCOUNT_SID
        twilio_api_key_sid = settings.TWILIO_API_KEY_SID
        twilio_api_key_secret = settings.TWILIO_API_KEY_SECRET

        client = TwilioRestClient(twilio_api_key_sid, twilio_api_key_secret)

        in_chat = False
        try:
            participants = client.video.rooms(patient_id).participants.get('provider').fetch()


            if participants:
                in_chat = True
        except Exception as e:
            in_chat = False

        data = { 'in_chat': in_chat }
        return HttpResponse(json.dumps(data), status=200, content_type='application/json')

    return HttpResponse(None, status=401)


def is_eighteen(request):
    if request.method == 'POST':
        data = {
            'is_eighteen': True,
        }

        dob = json.loads(request.body)['dob']

        try:
            dob_year, dob_month, dob_day = dob.split('-')
        except ValueError:
            return JsonResponse(data, safe=False)

        dob_year = int(dob_year)
        dob_month = int(dob_month)
        dob_day = int(dob_day)

        try:
            datetime(dob_year, dob_month, dob_day)
        except ValueError:
            return JsonResponse(data, safe=False)

        if dob_year > 1800 and dob_month > 0 and dob_day > 0:
            today = datetime.now()

            patient_age = today.year - dob_year - ((today.month, today.day) < (dob_month, dob_day))

            if patient_age < 18:
                data = {
                    'is_eighteen': False,
                }

        return JsonResponse(data, safe=False)

    return HttpResponse(None, status=401)


def is_holiday():
    today = datetime.now()

    if datetime.strftime(today, '%m/%d/%y') == '11/25/21':
        return True
    else:
        return False


def apply_coupon(request):
    if request.method == 'POST':
        patient_id = json.loads(request.body)['patient_id']
        coupon_code = json.loads(request.body)['coupon_code']
        coupon = None

        default_cost = 4995  # should have this come from the DB.
        loc_dt = datetime.now()

        if coupon_code:
            coupon = Coupon.objects.filter(code__iexact=coupon_code, begin_date__lte=loc_dt.today(), end_date__gte=loc_dt.today()).first()

        patient_cost = Patient_Cost.objects.filter(patient_id=patient_id).first()
        status = 'Invalid coupon'

        should_apply_coupon = False

        if coupon:
            if coupon.max_uses:
                if coupon.max_uses > coupon.current_uses:
                    should_apply_coupon = True
                else:
                    status = 'All coupons used'
            else:
                should_apply_coupon = True
        else:
            status = 'Coupon not found'

        if should_apply_coupon:
            patient_cost.cost = int(default_cost) - int(coupon.discount)
            patient_cost.coupon_applied = True
            patient_cost.coupon = coupon
            patient_cost.save(update_fields=['cost', 'coupon_applied', 'coupon'])
            status = 'Success'

        data = {
            'patient_cost': patient_cost.cost,
            'status_msg': status,
            'default_cost': default_cost
        }

        return JsonResponse(data, safe=False)

    return HttpResponse(None, status=401)


def patient_cost(request):
    if request.method == 'POST':
        patient_id = json.loads(request.body)['patient_id']

        patient_cost = Patient_Cost.objects.filter(patient_id=patient_id).first()

        data = {
            'patient_cost': patient_cost.cost,
        }

        return JsonResponse(data, safe=False)

    return HttpResponse(None, status=401)


def square_app_id(request):
    data = {
        'square_app_id': settings.SQUARE_APP_ID,
    }
    return JsonResponse(data, safe=False)


def server_time(request):
    server_time = datetime.now()
    loc_dt = server_time

    off_hours = is_offhours()

    provider_list = User.objects.filter(groups__name='Appointment Notifications').values('email')
    providers = []
    for email in provider_list:
        providers.append(email['email'])

    context = {
        'local_time': datetime.strftime(loc_dt, '%m/%d/%Y %H:%M'),
        'server_time': datetime.strftime(server_time, '%m/%d/%Y %H:%M'),
        'local_hour': datetime.strftime(loc_dt, '%H'),
        'off_hours': off_hours,
        'providers': providers,
    }
    return render(request, 'EasyConnect/server-time.html', context)


def is_offhours():
    loc_dt = datetime.now()

    # get day of week
    # 0 = Monday
    # 1 = Tuesday
    # 2 = Wednesday
    # 3 = Thursday
    # 4 = Friday
    # 5 = Saturday
    # 6 = Sunday
    day_of_week = loc_dt.weekday()

    if day_of_week in (0, 1, 2, 3, 4):
        start_time = 8
        end_time = 17
    else:
        return False

    off_hours = False

    if start_time < end_time:
        # e.g. if not (8 <= loc_dt.hour < 20):
        if not (start_time <= loc_dt.hour < end_time):
            off_hours = True
    else:
        if (end_time <= loc_dt.hour < start_time):
            off_hours = True

    return off_hours


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
                sym.pancreatitis_thyroid_cancer pancreatitis_thyroid_cancer, sym.allergies allergies, 
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
    app_search = "and eca.create_datetime >= now()::date - interval '18 hours'"
    if status == 'Appointment Complete':
        app_search = ""

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
            WHERE eca.status='{status}' {app_search}
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


def provider_joined(request):
    patient_id = json.loads(request.body)['patient_id']
    appointment = Appointments.objects.filter(patient_id=patient_id).order_by('-create_datetime').first()

    joined = True
    if appointment.status == 'Ready for Provider':
        joined = False
        send_provider_notification(patient_id, True)

    data = {'provider_joined': joined}

    return JsonResponse(data, safe=False)


def send_provider_notification(patient_id, reminder=False):
    patient = Patient.objects.filter(pk=patient_id).first()
    provider_list = User.objects.filter(groups__name='Appointment Notifications').values('email')
    providers = []
    for email in provider_list:
        providers.append(email['email'])

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

    if reminder:
        subject = f'Patient still waiting for provider {patient.first_name} {patient.last_name}'
    else:
        subject = f'Video Chat for {patient.first_name} {patient.last_name}'

    EmailThread(
        subject=subject,
        message=body,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=providers,
        fail_silently=False,
        html_message=html_body
    ).start()


def send_patient_notification(patient_id):
    patient = Patient.objects.filter(pk=patient_id).first()

    patient_cost = Patient_Cost.objects.filter(patient_id=patient_id).first()
    video_url = f'{settings.EMAIL_BASE_URL}/video-chat/{patient_id}'

    if int(patient_cost.cost) > 0:
        payment_info = Payment.objects.filter(patient_id=patient_id, status='Paid').values('response').first()['response']
        payment_info = json.loads(payment_info.replace("\'", "\""))

        payment_date = payment_info['payment']['created_at']
        payment_card_type = payment_info['payment']['card_details']['card']['card_brand']
        payment_card_last4 = payment_info['payment']['card_details']['card']['last_4']
        payment_amount = payment_info['payment']['amount_money']['amount'] / 100
    else:
        payment_date = datetime.today()
        payment_card_type = "NA"
        payment_card_last4 = "NA"
        payment_amount = "Free"

    #add call to sendgrid to send


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


def order_nonce(request):
    if request.method == 'POST':
        logger.info(f'Adding nonce to session.')
        nonce = json.loads(request.body)['nonce']
        request.session['nonce'] = nonce
        return HttpResponse('ok')

    return HttpResponseNotAllowed(['POST', ])
