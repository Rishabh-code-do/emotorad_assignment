from django.http import JsonResponse
from .models import Contact
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import json
import logging
import re


logger = logging.getLogger(__name__)

@csrf_exempt
@transaction.atomic
def identify(request):
    try:
        if request.method == 'POST':
            data = json.loads(request.body)
            email = data.get('email')
            email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

            if email and not re.match(email_regex, email):
                return JsonResponse({"error": "Incorrect contact information provided.(email)"}, status=400)
            
            phone_number = data.get('phoneNumber')
            number_regex = r'^[6-9]\d{9}$'
            
            if phone_number and not re.match(number_regex, phone_number):
                return JsonResponse({"error": "Incorrect contact information provided.(phone_number)"}, status=400)

            if not email and not phone_number:
                return JsonResponse({"error": "Insufficient contact information provided."}, status=400)
            response_data = merge_and_return_contact(email, phone_number)
            return JsonResponse(response_data, status=200)
        else:
            raise ValueError("Method not allowed")
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return JsonResponse({"error": "A temporal anomaly has occurred. Please try again later."}, status=400)

def merge_and_return_contact(email, phone):
    primary_contact = None
    secondary_contact = None

    if phone and email:
        primary_contact = Contact.objects.filter(email=email,phone_number=phone, link_precedence='primary').last()
    if primary_contact:
        emails, phone_numbers, secondary_contact_ids = gather_related_info(primary_contact)
        return {
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phone_numbers,
            "secondaryContactIds": secondary_contact_ids}

    if phone:
        primary_contact = Contact.objects.filter(phone_number=phone, link_precedence='primary').last()
    if not primary_contact and email:
        primary_contact = Contact.objects.filter(email=email, link_precedence='primary').last()
    
    
    if primary_contact:
        secondary_contact = Contact.objects.filter(email=email,phone_number=phone,link_precedence='secondary', linked_contact_id=primary_contact.id).last()
        if not secondary_contact:
            secondary_contact = Contact.objects.create(email=email,phone_number=phone,link_precedence='secondary',linked_contact_id=primary_contact.id)
    else:
        second_stage = None
        if phone:
            second_stage = Contact.objects.filter(phone_number=phone,link_precedence='secondary').last()
        if not second_stage and email:
            second_stage = Contact.objects.filter(email=email,link_precedence='secondary').last()
        if second_stage and second_stage.linked_contact:
            primary_contact = second_stage.linked_contact
            secondary_contact = Contact.objects.filter(email=email,phone_number=phone, link_precedence='secondary', linked_contact_id=second_stage.linked_contact.id).last()
            if not secondary_contact:
                secondary_contact = Contact.objects.create(email=email,phone_number=phone, link_precedence='secondary',linked_contact_id=second_stage.linked_contact.id)
    
    if secondary_contact:
        # Gather all related emails and phone numbers for the response
        emails, phone_numbers, secondary_contact_ids = gather_related_info(primary_contact)
        return {
            "primaryContactId": primary_contact.id,
            "emails": emails,
            "phoneNumbers": phone_numbers,
            "secondaryContactIds": secondary_contact_ids}
    else:
        new_contact = Contact.objects.create(phone_number=phone,email=email,link_precedence='primary',linked_contact=None)
        emails = [new_contact.email] if new_contact and new_contact.email else []
        phone_numbers = [new_contact.phone_number] if new_contact and new_contact.phone_number else []
        if new_contact:
            return {
                "primaryContactId": new_contact.id,
                "emails": emails,
                "phoneNumbers": phone_numbers,
                "secondaryContactIds": []
            }
        
    return {}

def gather_related_info(primary_contact):
    # Gather all emails, phone numbers, and secondary contact IDs
    emails = list(Contact.objects.filter(linked_contact=primary_contact).exclude(email=None).values_list('email', flat=True).distinct())
    phone_numbers = list(Contact.objects.filter(linked_contact=primary_contact).exclude(phone_number=None).values_list('phone_number', flat=True).distinct())
    secondary_contact_ids = list(Contact.objects.filter(linked_contact=primary_contact).values_list('id', flat=True).distinct())

    if primary_contact.email and primary_contact.email not in emails:
        emails.append(primary_contact.email)
    if primary_contact.phone_number and primary_contact.phone_number not in phone_numbers:
        phone_numbers.append(primary_contact.phone_number)

    return emails, phone_numbers, secondary_contact_ids