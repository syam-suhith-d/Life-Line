from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('create_request/', views.create_request_view, name='create_request'),
    path('pledge_organ/', views.pledge_organ_view, name='pledge_organ'),
    path('hospital_slots/', views.book_slot_view, name='book_slot'),
    path('search_donors/', views.search_donors_view, name='search_donors'),
    path('compatibility_checker/', views.compatibility_checker_view, name='compatibility'),
    path('smart_checker/', views.smart_eligibility_view, name='smart_checker'),
    path('certificate/', views.certificate_view, name='certificate'),
    path('about/', views.about_view, name='about'),
    path('contact/', views.contact_view, name='contact'),
    path('privacy-terms/', views.privacy_terms_view, name='privacy_terms'),
    path('admin-dashboard/', views.admin_dashboard_view, name='admin_dashboard'),
]