from django import forms
from django.core.validators import URLValidator
from django.utils.translation import gettext_lazy as _

class UrlSubmitForm(forms.Form):
    """
    Form for submitting a starting URL to crawl.
    """
    url = forms.URLField(
        label=_("Website URL"),
        required=True,
        max_length=2048,
        widget=forms.URLInput(attrs={
            'placeholder': 'https://example.com',
            'class': 'form-control' # Basic styling hook
        }),
        help_text=_("Enter the full starting URL (e.g., https://docs.example.com)")
    )

    max_pages = forms.IntegerField(
        label=_("Max Pages to Crawl"),
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Leave empty for no limit',
            'class': 'form-control'
        }),
        help_text=_("Optional limit on the number of pages to crawl for testing.")
    )

    max_depth = forms.IntegerField(
        label=_("Max Crawl Depth"),
        required=False,
        min_value=1,
        widget=forms.NumberInput(attrs={
            'placeholder': 'Leave empty for no limit',
            'class': 'form-control'
        }),
        help_text=_("Optional limit on the crawl depth for testing.")
    )

    restrict_to_path = forms.BooleanField(
        label=_("Restrict crawl to initial path?"),
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        help_text=_("If checked, only crawl pages under the same path as the starting URL (e.g., /docs/v1/).")
    )

    def clean_url(self):
        """
        Additional validation for the URL.
        Ensures it's a valid HTTP/HTTPS URL.
        """
        url = self.cleaned_data.get('url')
        if url:
            validator = URLValidator(schemes=['http', 'https'])
            try:
                validator(url)
            except forms.ValidationError:
                raise forms.ValidationError(_("Please enter a valid HTTP or HTTPS URL."), code='invalid_scheme')
        return url
