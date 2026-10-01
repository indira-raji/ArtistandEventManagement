from django import forms
from .models import EventManagement


class EventManagementForm(forms.ModelForm):

    class Meta:
        model = EventManagement
        fields = [
            "team_name",
            "owner_name",
            "email",
            "phone",
            "address",
            "city",
            "social_link",
            "experience",
            "languages",
            "logo",
            "description",
        ]