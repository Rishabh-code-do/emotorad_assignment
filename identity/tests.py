from django.test import TestCase, Client
from django.urls import reverse
from .models import Contact
import json
import random
import string

class CovertIdentifyViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('identify')  # Adjust if necessary
        self.existing_contact_email = self.generate_random_email()
        self.existing_contact_phone = self.generate_random_phone()
        self.contact = Contact.objects.create(
            email=self.existing_contact_email,
            phone_number=self.existing_contact_phone,
            link_precedence='primary'
        )

    def generate_random_email(self):
        return ''.join(random.choices(string.ascii_lowercase, k=10)) + "@example.com"

    def generate_random_phone(self):
        return ''.join(random.choices("6789", k=1) + random.choices(string.digits, k=9))


    def test_existing_contact_with_email(self):
        data = {
            "email": self.existing_contact_email,
            "phoneNumber": self.generate_random_phone()
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("primaryContactId", response_data)

    def test_existing_contact_with_phone(self):
        data = {
            "email": self.generate_random_email(),
            "phoneNumber": self.existing_contact_phone
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("primaryContactId", response_data)

    def test_contact_merging(self):
        data = {
            "email": self.existing_contact_email,
            "phoneNumber": self.existing_contact_phone
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("primaryContactId", response_data)
        # Ensure no new contact was created
        self.assertEqual(Contact.objects.count(), 1)

    def test_contact_creation_with_random_data(self):
        data = {
            "email": self.generate_random_email(),
            "phoneNumber": self.generate_random_phone()
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        response_data = response.json()
        self.assertIn("primaryContactId", response_data)

    def test_invalid_email_handling(self):
        data = {
            "email": "invalid-email",
            "phoneNumber": self.generate_random_phone()
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["error"], "Incorrect contact information provided.(email)")

    def test_invalid_phone_handling(self):
        data = {
            "email": self.generate_random_email(),
            "phoneNumber": "12345"
        }
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["error"], "Incorrect contact information provided.(phone_number)")

    def test_missing_contact_information(self):
        data = {}
        response = self.client.post(self.url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["error"], "Insufficient contact information provided.")

    def test_invalid_method_handling(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 400)
        response_data = response.json()
        self.assertEqual(response_data["error"], "A temporal anomaly has occurred. Please try again later.")

