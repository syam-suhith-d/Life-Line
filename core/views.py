from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.core.paginator import Paginator
from .models import UserProfile, BloodRequest, OrganPledge, OrganRequest, HospitalAppointment, Feedback, DonationCamp, Notification
from .forms import RegistrationForm, BloodRequestForm, OrganPledgeForm, OrganRequestForm, SmartEligibilityForm, HospitalAppointmentForm, FeedbackForm


def home_view(request):
    camps = DonationCamp.objects.filter(camp_date__gte=timezone.now().date()).order_by('camp_date')[:5]
    return render(request, 'home.html', {'camps': camps})


def about_view(request):
    return render(request, 'about.html')


def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            profile = UserProfile.objects.create(
                user=user,
                role=form.cleaned_data['role'],
                blood_group=form.cleaned_data['blood_group'],
                organ_pledge=form.cleaned_data['organ_pledge'],
                city=form.cleaned_data['city'],
                phone=form.cleaned_data['phone']
            )
            profile.save()
            # CHANGED: Removed auto-login. Redirect straight to login page.
            messages.success(request, 'Registration complete. Please log in.')
            return redirect('login') 
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # CHANGED: Redirect to home/index instead of dashboard
                # ADD THIS LINE: Trigger the toast message
                messages.success(request, f'Welcome back, {user.username}! Login successful.')
                
                return redirect('home') 
            messages.error(request, 'Invalid username or password.')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


# 1. The Normal Dashboard (Now available to everyone, including Admins)
@login_required
def dashboard_view(request):
    # This safely gets the profile, or automatically creates a placeholder one for admins!
    profile, created = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={
            'role': 'Admin',
            'blood_group': 'N/A',
            'organ_pledge': 'None',
            'city': 'System Admin',
            'phone': 'N/A'
        }
    )
    
    appointments = HospitalAppointment.objects.filter(user=request.user).order_by('appointment_date')
    requests = BloodRequest.objects.filter(user=request.user).order_by('-id')[:5]
    
    return render(request, 'dashboard.html', {
        'profile': profile,
        'appointments': appointments,
        'requests': requests,
    })
    
# 2. The Brand New Admin-Only Dashboard View
@login_required
def admin_dashboard_view(request):
    # Kick out normal users if they try to access this URL
    if not (request.user.is_staff or request.user.is_superuser):
        return redirect('dashboard')
        
    total_donors = UserProfile.objects.filter(role='Donor').count()
    total_organ_donors = UserProfile.objects.exclude(organ_pledge='None').count()
    total_appointments = HospitalAppointment.objects.count()
    
    # Pagination Logic
    donor_list = UserProfile.objects.filter(role='Donor').order_by('-id')
    paginator = Paginator(donor_list, 10)
    page_number = request.GET.get('page')
    donors = paginator.get_page(page_number)
    
    # Grab only the 5 most recent requests and appointments to save server memory!
    requests = BloodRequest.objects.all().order_by('-id')[:5]
    appointments = HospitalAppointment.objects.all().order_by('-appointment_date')[:5]
    
    return render(request, 'dashboard_admin.html', {
        'total_donors': total_donors,
        'total_organ_donors': total_organ_donors,
        'total_appointments': total_appointments,
        'donors': donors,
        'requests': requests,
        'appointments': appointments,
    })


@login_required
def create_request_view(request):
    if request.method == 'POST':
        form = BloodRequestForm(request.POST)
        if form.is_valid():
            blood_req = form.save(commit=False)
            if request.user.is_authenticated:
                blood_req.user = request.user
            blood_req.save()
            messages.success(request, 'Urgent blood request registered successfully.')
            return redirect('dashboard')
    else:
        form = BloodRequestForm()
    return render(request, 'form_template.html', {'form': form, 'title': 'Raise Urgent Blood Request'})


@login_required
def pledge_organ_view(request):
    if request.method == 'POST':
        form = OrganPledgeForm(request.POST)
        if form.is_valid():
            pledge = form.save(commit=False)
            pledge.donor = request.user
            pledge.save()
            # increment life-saving score for donor
            try:
                profile = UserProfile.objects.get(user=request.user)
                profile.life_saving_score = max(0, profile.life_saving_score)
                profile.save()
            except UserProfile.DoesNotExist:
                pass
            messages.success(request, 'Organ pledge submitted successfully.')
            return redirect('dashboard')
    else:
        form = OrganPledgeForm()
    return render(request, 'form_template.html', {'form': form, 'title': 'Pledge Your Organs for Donation'})


@login_required
def book_slot_view(request):
    if request.method == 'POST':
        form = HospitalAppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save(commit=False)
            appointment.user = request.user
            appointment.save()
            messages.success(request, 'Your hospital time slot booking is confirmed.')
            return redirect('dashboard')
    else:
        form = HospitalAppointmentForm()
    return render(request, 'slot_booking.html', {'form': form, 'title': 'Book Blood Donation Time Slot'})


def search_donors_view(request):
    blood_group = request.GET.get('blood_group')
    city = request.GET.get('city')
    q = request.GET.get('q', '').strip()
    donors = UserProfile.objects.filter(role='Donor')
    if blood_group:
        donors = donors.filter(blood_group=blood_group)
    if city:
        donors = donors.filter(city__icontains=city)

    # phonetic (Soundex) matching for name/city query
    def soundex(name: str) -> str:
        if not name:
            return ''
        name = name.upper()
        mapping = {"B": "1", "F": "1", "P": "1", "V": "1",
                   "C": "2", "G": "2", "J": "2", "K": "2", "Q": "2", "S": "2", "X": "2", "Z": "2",
                   "D": "3", "T": "3",
                   "L": "4",
                   "M": "5", "N": "5",
                   "R": "6"}
        first = name[0]
        tail = ''.join(mapping.get(ch, '') for ch in name[1:])
        # remove duplicates
        cleaned = first
        prev = ''
        for ch in tail:
            if ch != prev:
                cleaned += ch
                prev = ch
        # remove zeros and pad
        cleaned = (cleaned + '000')[:4]
        return cleaned

    phonetic_matches = []
    if q:
        q_s = soundex(q)
        for d in list(donors):
            name_s = soundex(d.user.username)
            if q.lower() in d.user.username.lower() or q.lower() in d.city.lower() or (q_s and name_s == q_s):
                phonetic_matches.append(d)
        donors = phonetic_matches

    blood_groups = ['A+', 'A-', 'B+', 'B-', 'O+', 'O-', 'AB+', 'AB-']
    return render(request, 'search.html', {
        'donors': donors,
        'q': q,
        'blood_group': blood_group,
        'city': city,
        'blood_groups': blood_groups,
    })


def smart_eligibility_view(request):
    result = None
    reasons = []
    if request.method == 'POST':
        form = SmartEligibilityForm(request.POST)
        if form.is_valid():
            age = form.cleaned_data['age']
            weight = form.cleaned_data['weight']
            hemoglobin = form.cleaned_data['hemoglobin']
            last = form.cleaned_data.get('last_donation_date')
            # rules
            if age < 18 or age > 65:
                reasons.append('Age outside allowed range (18-65).')
            if weight < 50:
                reasons.append('Weight below 50kg.')
            if hemoglobin < 12.5:
                reasons.append('Hemoglobin below 12.5 g/dL.')
            if last:
                delta = (timezone.now().date() - last).days
                if delta < 90:
                    reasons.append('Last donation was less than 90 days ago.')
            if reasons:
                result = False
            else:
                result = True
    else:
        form = SmartEligibilityForm()
    return render(request, 'smart_checker.html', {'form': form, 'result': result, 'reasons': reasons})


@login_required
def certificate_view(request):
    profile = get_object_or_404(UserProfile, user=request.user)
    return render(request, 'certificate.html', {'profile': profile})


def compatibility_checker_view(request):
    matrix = {
        'A+': {'receive': ['A+', 'A-', 'O+', 'O-'], 'give': ['A+', 'AB+']},
        'A-': {'receive': ['A-', 'O-'], 'give': ['A+', 'A-', 'AB+', 'AB-']},
        'B+': {'receive': ['B+', 'B-', 'O+', 'O-'], 'give': ['B+', 'AB+']},
        'B-': {'receive': ['B-', 'O-'], 'give': ['B+', 'B-', 'AB+', 'AB-']},
        'O+': {'receive': ['O+', 'O-'], 'give': ['A+', 'B+', 'O+', 'AB+']},
        'O-': {'receive': ['O-'], 'give': ['All Blood Groups']},
        'AB+': {'receive': ['All Blood Groups'], 'give': ['AB+']},
        'AB-': {'receive': ['A-', 'B-', 'O-', 'AB-'], 'give': ['AB+', 'AB-']}
    }
    selected_bg = request.GET.get('blood_group')
    results = None
    available_count = 0
    if selected_bg and selected_bg in matrix:
        results = matrix[selected_bg]
        donors_qs = UserProfile.objects.filter(role='Donor')
        if selected_bg != 'AB+':
            donors_qs = donors_qs.filter(blood_group__in=matrix[selected_bg]['receive'])
        available_count = donors_qs.count()
    return render(request, 'compatability.html', {
        'results': results,
        'selected_bg': selected_bg,
        'available_count': available_count,
        'blood_groups': matrix.keys()
    })


def contact_view(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your feedback. We will review it promptly.')
            return redirect('contact')
    else:
        form = FeedbackForm()
    return render(request, 'contact.html', {'form': form})

def privacy_terms_view(request):
    return render(request, 'privacy_terms.html')  # Adjust path to 'privacy_terms.html' if not using a 'core' subfolder