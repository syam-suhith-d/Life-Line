from django.contrib import admin
from .models import UserProfile, BloodRequest, OrganPledge, Feedback, DonationSlot, HospitalAppointment, DonationCamp, Notification, OrganRequest


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
	list_display = ('user', 'role', 'blood_group', 'city', 'donor_id')
	search_fields = ('user__username', 'city', 'donor_id')


@admin.register(BloodRequest)
class BloodRequestAdmin(admin.ModelAdmin):
	list_display = ('patient_name', 'blood_group', 'priority', 'status', 'timestamp')
	list_filter = ('priority', 'status')


admin.site.register(OrganPledge)
admin.site.register(OrganRequest)
admin.site.register(Feedback)
admin.site.register(DonationSlot)
admin.site.register(DonationCamp)
admin.site.register(HospitalAppointment)
admin.site.register(Notification)
