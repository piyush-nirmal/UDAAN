from django.urls import path
from . import views
urlpatterns = [
    path('donor-search/', views.index, name='index'),
    path('api/register/', views.register_donor, name='register_donor'),
    path('api/search/', views.search_donors, name='search_donors'),
    path('api/certificate/lookup/', views.certificate_lookup, name='certificate_lookup'),
    path('api/notes/', views.personal_notes_api, name='personal_notes_api'),
    path('projects/', views.projects_page, name='projects'),

    path('reports/', views.report_list, name='report_list'),
    path('blogs/<int:id>/', views.blog_detail, name='blog_detail'),
    path('donor/<int:pk>/', views.donor_detail, name='donor_detail'),


    path(
    'career-and-fellowship/',
    views.career_fellowship,
    name='career_fellowship'
),


    path('locations/', views.locations, name='locations'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/create/', views.appointment_create, name='appointment_create'),
      path(
        'campus-ambassador/',
        views.campus_ambassador,
        name='campus_ambassador'
    ),
    path("jobs/", views.jobs, name="jobs"),
    path('internships/', views.internships, name='internships'),

    # path(
    #     'ambassador/<int:id>/',
    #     views.ambassador_detail,
    #     name='ambassador_detail'
    # ),

   path('about-us/', views.aboutus, name='aboutus'),
   path('our-mission-values/', views.our_mission_values, name='our_mission_values'),

     path('', views.home_view, name='home'),

    path('contact-us/', views.contact_us, name='contact_us'),
    path('our-team/', views.our_team, name='our_team'),
    path('faq/', views.faq, name='faq'),
    path('our-partners/', views.our_partners, name='our_partners'),
    path('appreciation-and-accolades/', views.appreciationandaccolades, name='appreciationandaccolades'),
    path('our-activities/', views.our_activities, name='our_activities'),
     path("blood-donation/", views.blood_donation, name="blood_donation"),
     path("api/ngo/register/", views.ngo_register, name="ngo_register"),
    path("api/bloodbank/register/", views.bloodbank_register, name="bloodbank_register"),
    path("api/camp-rsvp/", views.camp_rsvp, name="camp_rsvp"),
    path("api/alerts/subscribe/", views.alerts_subscribe, name="alerts_subscribe"),
    path("api/blood-request/", views.blood_request_submit, name="blood_request_submit"),
     path("api/newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
]
