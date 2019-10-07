from django import forms

class CreateAuctionForm(forms.Form):
    title=forms.CharField(max_length=256)
    description=forms.CharField(widget=forms.Textarea())
    minimum_price=forms.FloatField(label="minimum_price",min_value=0.01)
    deadline_date = forms.DateTimeField(input_formats=['%d.%m.%Y %H:%M:%S', ],
                                       widget=forms.TextInput(attrs={"placeholder": "dd.mm.yyyy HH:MM:SS"}),
                                       help_text="The format of the date should be dd.mm.yyyy HH:MM:SS",
                                       label="Deadline Date")