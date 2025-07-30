from django import forms
from common import models

class TicketRasing(forms.ModelForm):
    class Meta:
        model=models.Ticketing
        fields=['ticketdesc','ticketsubj','ticketfile','ticketpriority']
        labels = {
            'ticketsubj': 'Subject',
            'ticketdesc': 'Description',
            'ticketpriority': 'Priority',
            'ticketfile': 'Attachment (Optional)',
        }