from django import forms

class CreateAuctionForm(forms.Form):
    title=forms.CharField(required=True)
    body=forms.CharField(widget=forms.Textarea())