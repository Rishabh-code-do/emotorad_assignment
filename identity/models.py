from django.db import models
from django.utils import timezone

class Contact(models.Model):
    email = models.EmailField(null=True, blank=True, db_index=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True, db_index=True)
    linked_contact = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='secondary_contacts')
    link_precedence = models.CharField(max_length=10, choices=[('primary', 'Primary'), ('secondary', 'Secondary')], default='primary')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Contact {self.id} - {self.email or self.phone_number}  (Primary ID: {self.linked_contact_id or self.id})"

    class Meta:
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['phone_number']),
            models.Index(fields=['email', 'phone_number']),
        ]
