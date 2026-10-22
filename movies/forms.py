from django import forms
from .models import Review

class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(min_value=1, max_value=10)

    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {"text": forms.Textarea(attrs={"rows": 3, "placeholder": "Enter your review about this movie"})}