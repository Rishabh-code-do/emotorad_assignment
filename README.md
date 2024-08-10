# Contact Identification API

This Django project provides an API endpoint to identify and merge contact information based on email and phone numbers. It supports storing and retrieving contacts, where contacts can have either primary or secondary precedence.

## Features

- **Contact Creation**: Allows for the creation of contacts using email and/or phone numbers.
- **Contact Merging**: Merges contacts with the same email or phone number under a single primary contact, while others are designated as secondary contacts.
- **Validation**: Ensures that only valid email addresses and Indian phone numbers are accepted.

## Requirements

- Python 3.7+
- Django 3.0+
- SQLite (for development)
  
## Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/yourusername/contact-identification-api.git
   cd emotorad_assignment

2. **Apply Migrations:**:
   ```bash
   python manage.py migrate
   
3. **Run the Server:**:
   ```bash
   python manage.py runserver


## API Endpoint

### Identify Contact

**URL**: `/identify/`

**Method**: `POST`

**Description**: This endpoint takes an email and/or phone number as input, validates them, and returns information about the associated primary contact, along with any linked secondary contacts.

**Request Body**:
```json
{
  "email": "user@example.com",
  "phoneNumber": "9876543210"
}
```
- **email**: (optional) The email address of the contact.
- **phoneNumber**: (optional) The phone number of the contact.

**Response**:
```json
{
  "primaryContactId": 1,
  "emails": ["user@example.com"],
  "phoneNumbers": ["9876543210"],
  "secondaryContactIds": [2, 3]
}
```

- **primaryContactId**: The ID of the primary contact.
- **emails**: A list of all emails associated with the primary contact.
- **phoneNumbers**: A list of all phone numbers associated with the primary contact.
- **secondaryContactIds**: A list of IDs of all secondary contacts linked to the primary contact.

## Error Responses

**400 Bad Request**: This status code is returned if the email or phone number is invalid, or if neither is provided.

- **Example error response for invalid email**:
  ```json
  {
    "error": "Incorrect contact information provided.(email)"
  }
- **Example error response for invalid phone number**:
  ```json
  {
  "error": "Incorrect contact information provided.(phone_number)"
  }

- **Example error response for missing email and phone number**:
  ```json
  {
  "error": "Insufficient contact information provided."
  }

## Running Tests

Unit tests are included to validate the functionality of the API.

**Run Tests**:
```bash
python manage.py test
```

## Logging

Logging is configured to capture any errors that occur during the identification process. Logs are useful for debugging purposes and help in tracking issues that may arise during the execution of the API. By default, errors are logged using Django's built-in logging framework.

Logs can be found in the location specified in your Django settings file under the `LOGGING` configuration. Ensure that the logging level is set appropriately to capture the required level of detail.

## Indexes

Database indexes are created on the `email` and `phone_number` fields to improve querying performance and optimize database operations.

The indexes defined in the `Contact` model are:

- **Email Index**: Improves query performance on the `email` field.
- **Phone Number Index**: Improves query performance on the `phone_number` field.
- **Composite Index**: Optimizes queries that filter on both `email` and `phone_number` fields together.

These indexes are specified in the `Meta` class of the `Contact` model to ensure efficient data retrieval and manipulation.

