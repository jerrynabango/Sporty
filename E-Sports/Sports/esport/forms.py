from django import forms
from .models import Comment, ContactMessage


class CommentForm(forms.ModelForm):
    """
    Comment form.
    """
    class Meta:
        model = Comment
        fields = ['text']


"""class ContactForm(forms.Form):
    name = forms.CharField(label='Your Name', max_length=100)
    email = forms.EmailField(label='Your Email')
    message = forms.CharField(label='Your Message', widget=forms.Textarea)
"""


class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'message']
