from django import forms
from .models import Auction
from django.forms import ModelForm
from . import models


class CreateAuctionForm(forms.Form):
    title=forms.CharField(max_length=256)
    description=forms.CharField(widget=forms.Textarea())
    minimum_price=forms.FloatField(label="minimum_price",min_value=0.01)
    deadline_date = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M:%S', ],
                                       widget=forms.TextInput(attrs={"placeholder": "dd.mm.yyyy HH:MM:SS"}),
                                       help_text="The format of the date should be dd.mm.yyyy HH:MM:SS",
                                       label="Deadline Date")
    hosted_by=forms.CharField(max_length=40, widget=forms.HiddenInput(),required=False)

class EditAuctionForm(forms.Form):
    title=forms.CharField(max_length=256)
    description=forms.CharField(widget=forms.Textarea())