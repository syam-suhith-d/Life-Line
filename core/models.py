from django.db import models
from django.contrib.auth.models import User
import qrcode
from io import BytesIO
from django.core.files import File
from PIL import Image
import uuid
from django.utils import timezone

ROLE_CHOICES = [('Donor', 'Donor'), ('Recipient', 'Recipient')]
BLOOD_GROUPS = [('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('O+', 'O+'), ('O-', 'O-'), ('AB+', 'AB+'), ('AB-', 'AB-')]
ORGAN_CHOICES = [('None', 'None'), ('Heart', 'Heart'), ('Kidney', 'Kidney'), ('Liver', 'Liver'), ('Lungs', 'Lungs'), ('Eyes', 'Eyes'), ('Pancreas', 'Pancreas')]
STATUS_CHOICES = [('Pending', 'Pending'), ('Approved', 'Approved')]
DONATION_TIME_CHOICES = [('Morning', 'Morning'), ('Afternoon', 'Afternoon')]
HOSPITAL_CHOICES = [
    ('City Medical Center', 'City Medical Center'),
    ('Central Health Hospital', 'Central Health Hospital'),
    ('National Care Institute', 'National Care Institute'),
    ('Riverbank General Hospital', 'Riverbank General Hospital'),
    ('Pioneer Trauma Center', 'Pioneer Trauma Center'),
]
APPOINTMENT_SLOT_CHOICES = [
    ('09:00 AM - 12:00 PM', '09:00 AM - 12:00 PM'),
    ('12:00 PM - 03:00 PM', '12:00 PM - 03:00 PM'),
    ('03:00 PM - 06:00 PM', '03:00 PM - 06:00 PM'),
]

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    donor_id = models.CharField(max_length=32, unique=True, blank=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    organ_pledge = models.CharField(max_length=50, choices=ORGAN_CHOICES, default='None')
    city = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    last_donation_date = models.DateField(null=True, blank=True)
    life_saving_score = models.IntegerField(default=0)
    qr_code = models.ImageField(upload_to="qr_codes/", blank=True)

    def save(self, *args, **kwargs):
        # ensure donor id present
        if not self.donor_id:
            self.donor_id = f"LL-{uuid.uuid4().hex[:10].upper()}"

        qr_text = (
            f"Name: {self.user.username}\n"
            f"ID: {getattr(self, 'donor_id', '')}\n"
            f"Role: {self.role}\n"
            f"Blood: {self.blood_group}\n"
            f"Organ: {self.organ_pledge}\n"
            f"Phone: {self.phone}"
        )
        qr_image = qrcode.make(qr_text)
        qr_image = qr_image.convert('RGB')
        # Pillow resampling compatibility
        try:
            resample = Image.Resampling.LANCZOS
        except Exception:
            resample = Image.LANCZOS if hasattr(Image, 'LANCZOS') else Image.BICUBIC
        qr_image = qr_image.resize((290, 290), resample)
        canvas = Image.new('RGB', (290, 290), 'white')
        canvas.paste(qr_image, (0, 0, 290, 290))
        fname = f"qr_code-{self.user.username}.png"
        buffer = BytesIO()
        canvas.save(buffer, 'PNG')
        buffer.seek(0)
        self.qr_code.save(fname, File(buffer), save=False)
        canvas.close()
        super().save(*args, **kwargs)

    @property
    def badge(self):
        s = self.life_saving_score or 0
        if s >= 50:
            return 'Gold Donor'
        if s >= 30:
            return 'Silver Donor'
        if s >= 10:
            return 'Bronze Donor'
        return 'Regular Member'

    def __str__(self):
        return f"{self.user.username} - {self.role}"

class BloodRequest(models.Model):
    PRIORITY_CHOICES = [('Critical', 'Critical'), ('High', 'High'), ('Normal', 'Normal')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blood_requests')
    patient_name = models.CharField(max_length=100)
    blood_group = models.CharField(max_length=5, choices=BLOOD_GROUPS)
    hospital_details = models.TextField()
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='Normal')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"BloodRequest({self.blood_group}) for {self.patient_name}"

class OrganPledge(models.Model):
    ORGAN_CHOICES = [('Kidney', 'Kidney'), ('Liver', 'Liver'), ('Heart', 'Heart'), ('Cornea', 'Cornea')]
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    organ_name = models.CharField(max_length=50, choices=ORGAN_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')

    def __str__(self):
        return f"{self.donor.username} pledged {self.organ_name}"

class OrganRequest(models.Model):
    VERIFICATION_STATUS = [('Hospital Verification Pending', 'Hospital Verification Pending'), ('Verified', 'Verified')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organ_requests')
    organ_needed = models.CharField(max_length=50, choices=ORGAN_CHOICES)
    hospital_name = models.CharField(max_length=200)
    verification_status = models.CharField(max_length=80, choices=VERIFICATION_STATUS, default='Hospital Verification Pending')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OrganRequest({self.organ_needed}) for {self.user.username}"

class Feedback(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()

    def __str__(self):
        return f"Feedback from {self.name}"

class DonationSlot(models.Model):
    donor = models.ForeignKey(User, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=200)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=20, choices=DONATION_TIME_CHOICES)

    def __str__(self):
        return f"{self.donor.username} slot at {self.hospital_name} on {self.appointment_date}"

class HospitalAppointment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hospital_name = models.CharField(max_length=100, choices=HOSPITAL_CHOICES)
    appointment_date = models.DateField()
    time_slot = models.CharField(max_length=30, choices=APPOINTMENT_SLOT_CHOICES)

    def __str__(self):
        return f"{self.user.username} @ {self.hospital_name} on {self.appointment_date} {self.time_slot}"

class DonationCamp(models.Model):
    title = models.CharField(max_length=200)
    location = models.CharField(max_length=200)
    camp_date = models.DateField()
    contact_number = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.title} @ {self.location} on {self.camp_date}"

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification to {self.user.username} @ {self.timestamp}"
