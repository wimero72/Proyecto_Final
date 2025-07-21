from django.urls import path
from . import views

urlpatterns = [
    path('ofertas/', views.job_offer_list, name='job_offer_list'),
    path('oferta/<int:offer_id>/', views.job_offer_detail, name='job_offer_detail'),
    path('oferta/<int:offer_id>/postular/', views.apply_to_offer, name='apply_to_offer'),
    path('oferta/crear/', views.create_offer, name='create_offer'),
    path('headhunter/', views.headhunter_dashboard, name='headhunter_dashboard'),
    path('headhunter/oferta/<int:offer_id>/candidaturas/', views.offer_applications, name='offer_applications'),
    path('headhunter/candidatura/<int:candidature_id>/update/',views.cambiar_estado_candidatura,name='cambiar_estado_candidatura'),
    path('headhunter/candidaturas/', views.candidature_list, name='candidature_list'),
    path('mensaje/<int:offer_id>', views.message, name='message'),
    path('headhunter/agenda/', views.agenda_semanal, name='agenda'),
    path('headhunter/api/acciones/', views.api_acciones_headhunter,name='api_acciones_headhunter'),
    path('headhunter/crear-accion/', views.crear_accion_ajax, name='crear_accion_ajax'),
    path('headhunter/agenda/mover/<int:pk>/', views.mover_accion_ajax,name='mover_accion_ajax'),
    
]