from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, BloodRequest, OrganPledge, OrganRequest, HospitalAppointment, Feedback, DonationCamp, ORGAN_CHOICES


class RegistrationForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter Password'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter Email'}))
    role = forms.ChoiceField(choices=[('Donor', 'Donor'), ('Recipient', 'Recipient')], widget=forms.Select(attrs={'class': 'form-select'}))
    blood_group = forms.ChoiceField(choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')], widget=forms.Select(attrs={'class': 'form-select'}))
    organ_pledge = forms.ChoiceField(choices=ORGAN_CHOICES, initial='None', widget=forms.Select(attrs={'class': 'form-select'}))
    city = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter City Name'}))
    phone = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Phone Number'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # strip any help_text to keep forms clean
        for field in self.fields.values():
            field.help_text = None


class BloodRequestForm(forms.ModelForm):
    class Meta:
        model = BloodRequest
        fields = ['patient_name', 'blood_group', 'hospital_details', 'priority']
        widgets = {
            'patient_name': forms.TextInput(attrs={'class': 'form-control'}),
            'blood_group': forms.Select(attrs={'class': 'form-select'}),
            'hospital_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None


class OrganRequestForm(forms.ModelForm):
    class Meta:
        model = OrganRequest
        fields = ['organ_needed', 'hospital_name']
        widgets = {
            'organ_needed': forms.Select(attrs={'class': 'form-select'}),
            'hospital_name': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None


class OrganPledgeForm(forms.ModelForm):
    class Meta:
        model = OrganPledge
        fields = ['organ_name']
        widgets = {
            'organ_name': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None


class SmartEligibilityForm(forms.Form):
    age = forms.IntegerField(widget=forms.NumberInput(attrs={'class': 'form-control', 'min': 0}))
    weight = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}))
    hemoglobin = forms.FloatField(widget=forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1'}))
    last_donation_date = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None


class HospitalAppointmentForm(forms.ModelForm):
    appointment_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}))

    class Meta:
        model = HospitalAppointment
        fields = ['hospital_name', 'appointment_date', 'time_slot']
        widgets = {
            'hospital_name': forms.Select(attrs={'class': 'form-select'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'email', 'message']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your message'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.help_text = None