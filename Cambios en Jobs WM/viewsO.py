from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import JobOffer, Candidatura, StatusMessageTemplate, CANDIDATURE_STATUS_CHOICES, AgendaAccion
from .forms import JobOfferForm, CandidatureStatusForm, CambiarEstadoCandidaturaForm, StatusMessageTemplateForm, AgendaAccionForm
from django.contrib import messages
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils.timezone import localtime, datetime
from django.views.decorators.csrf import csrf_exempt
from collections import defaultdict
import json



@login_required
def create_offer(request):
    if not request.user.groups.filter(name='headhunter').exists():
        messages.error(request, "Solo los headhunters pueden crear ofertas.")
        return redirect('home')

    if request.method == 'POST':
        form = JobOfferForm(request.POST)
        if form.is_valid():
            offer = form.save(commit=False)
            offer.created_by = request.user
            offer.save()
            messages.success(request, "Oferta creada correctamente.")
            return redirect('job_offer_list')  
    else:
        form = JobOfferForm()

    return render(request, 'jobs/create_offer.html', {'form': form})

def job_offer_list(request):

    offers = JobOffer.objects.filter(is_active=True).order_by('-created_at')
    offers = JobOffer.objects.all()

    # Comprobamos si el usuario es headhunter
    is_headhunter = request.user.groups.filter(name='headhunter').exists()
    

    return render(request, 'jobs/job_offer_list.html', {
        'offers': offers,
        'is_headhunter': is_headhunter,
    })
   


def job_offer_detail(request, offer_id):
    offer = get_object_or_404(JobOffer, id=offer_id)
    return render(request, 'jobs/job_offer_detail.html', {'offer': offer})


@login_required
def apply_to_offer(request, offer_id):
    offer = get_object_or_404(JobOffer, id=offer_id)
    # Evita duplicados
    existing = Candidatura.objects.filter(offer=offer, user=request.user).exists()
    if not existing:
        Candidatura.objects.create(offer=offer, user=request.user, estado='pendiente')
        messages.success(request, 'Has postulado correctamente.')
        return redirect('job_offer_detail', offer_id=offer.id)

    return render(request, 'jobs/apply_to_offer.html', {'offer': offer})

@login_required
def headhunter_dashboard(request):
    if not request.user.groups.filter(name='headhunter').exists():
        messages.error(request, "Acceso restringido al rol headhunter.")
        return redirect('home')

    offers = JobOffer.objects.filter(created_by=request.user)
    candidaturas = Candidatura.objects.filter(offer__in=offers).select_related('offer', 'user')

    if request.method == 'POST':
        candidature_id = request.POST.get('candidature_id')
        candidatura = Candidatura.objects.get(id=candidature_id)
        form = CandidatureStatusForm(request.POST, instance=candidatura)

        if form.is_valid():
            form.save()

            # Enviar email al candidato
            estado_humano = candidatura.get_estado_display()
            asunto = f"Actualización de tu candidatura a {candidatura.offer.title}"
            mensaje = f"""
Hola {candidatura.user.first_name or candidatura.user.username},

Tu candidatura para el puesto '{candidatura.offer.title}' ha sido actualizada al estado: {estado_humano}.

Gracias por usar nuestra plataforma OpenToJob.

Un saludo,  
El equipo de OpenToJob
"""
            send_mail(
                subject=asunto,
                message=mensaje,
                from_email=None,
                recipient_list=[candidatura.user.email],
                fail_silently=True,
            )
            return redirect('headhunter_dashboard')

    else:
        forms_dict = {c.id: CandidatureStatusForm(instance=c) for c in candidaturas}
    return render(request, 'jobs/headhunter_dashboard.html', {
        'candidaturas': candidaturas,
        'forms_dict': forms_dict,
    })
@login_required
def editar_plantilla_estado(request, estado):
    template, created = StatusMessageTemplate.objects.get_or_create(
        user=request.user,
        estado=estado
    )
    
    if request.method == 'POST':
        form = StatusMessageTemplateForm(request.POST, instance=template)
        if form.is_valid():
            form.save()
            return redirect('mis_plantillas_estado')
    else:
        form = StatusMessageTemplateForm(instance=template)
        
    return render(request, 'jobs/editar_plantilla.html', {'form': form, 'estado': estado})
@login_required
def offer_applications(request, offer_id):
    offer = get_object_or_404(JobOffer, id=offer_id, created_by=request.user)
    applications = offer.applications.all()
    return render(request, 'jobs/offer_applications.html', {
        'offer': offer,
        'applications': applications
    })

@login_required
def cambiar_estado_candidatura(request, candidature_id):
    print(f"Entrando a cambiar_estado_candidatura con id: {candidature_id}")
    candidatura = get_object_or_404(Candidatura, id=candidature_id)

    if request.method == 'POST':
        form = CambiarEstadoCandidaturaForm(request.POST, instance=candidatura)
        if form.is_valid():
            form.save()
            return redirect('job_offer_detail', offer_id=candidatura.offer.pk)
    else:
        # Cargar mensaje por defecto desde plantilla si existe
        try:
            plantilla = StatusMessageTemplate.objects.get(
                user=request.user,
                estado=candidatura.estado
            )
            default_message = plantilla.mensaje
        except StatusMessageTemplate.DoesNotExist:
            default_message = ''
        
        form = CambiarEstadoCandidaturaForm(
            instance=candidatura,
            initial={'mensaje_personalizado': default_message}
        )
    print("Renderizando template con formulario")
    return render(
        request,
        'jobs/cambiar_estado_candidatura.html',
        {'form': form, 'candidatura': candidatura}
    )

def candidature_list(request):
    candidatures = Candidatura.objects.all()
    return render(request, 'jobs/candidature_list.html', {'candidatures': candidatures})

def message(request, offer_id):
    return render(request, 'jobs/message.html' , {'offer_id': offer_id})

@login_required
def editar_plantilla_estado(request, estado):
    template, created = StatusMessageTemplate.objects.get_or_create(
        user=request.user,
        estado=estado
    )

    if request.method == 'POST':
        form = StatusMessageTemplateForm(request.POST, instance=template)

        if form.is_valid():
            form.save()
            return redirect('mis_plantillas_estado')
    else:
        form = StatusMessageTemplateForm(instance=template)

    return render(
        request,
        'jobs/editar_plantilla.html',
        {'form': form, 'estado': estado}
    )

@login_required
def agregar_accion(request, oferta_id):
    oferta = get_object_or_404(JobOffer, id=oferta_id)

    if request.method == 'POST':
        form = AgendaAccionForm(request.POST)
        if form.is_valid():
            accion = form.save(commit=False)
            accion.oferta = oferta
            accion.realizada_por = request.user
            accion.save()
            return redirect('detalle_oferta', pk=oferta.id)
    else:
        form = AgendaAccionForm()

    return render(request, 'jobs/agregar_accion.html', {
        'form': form,
        'oferta': oferta
    })

@login_required
def historial_acciones(request, oferta_id):
    oferta = get_object_or_404(JobOffer, id=oferta_id)
    acciones = AgendaAccion.objects.filter(oferta=oferta).order_by('-fecha')
    
    return render(request, 'jobs/historial_acciones.html', {
        'oferta': oferta,
        'acciones': acciones
    })

@login_required
def api_acciones_headhunter(request):
    acciones = AgendaAccion.objects.filter(user=request.user)
    eventos = []

    for accion in acciones:
        eventos.append({
            'title': f"{accion.get_tipo_display()} - {accion.oferta.title if accion.oferta else 'Sin oferta asociada'}",
            'start': accion.fecha.isoformat(),
            'url': '',  # Puedes poner aquí la URL al detalle si la tienes
            'color': get_color(accion.tipo),
        })

    return JsonResponse(eventos, safe=False)

def get_color(tipo):
    colores = {
        'llamada': '#007bff',
        'entrevista': '#28a745',
        'nota': '#6c757d',
        'seguimiento': '#ffc107',
        'otro': '#17a2b8',
    }
    return colores.get(tipo, '#343a40')  # Color por defecto

@login_required
def agenda_headhunter(request):
    return render(request, 'jobs/agenda.html')

@login_required
def agenda_semanal(request):
    acciones = AgendaAccion.objects.filter(user=request.user).order_by('fecha')
    form = AgendaAccionForm()

     # Agrupa acciones por día
    acciones_por_dia = defaultdict(list)
    for accion in acciones:
        acciones_por_dia[str(accion.fecha)] += [accion]

    return render(request, 'jobs/agenda.html', {
        'acciones_por_dia': acciones_por_dia,
        'form': form
    })

@login_required
def crear_accion_ajax(request):
    if request.method == 'POST':
        form = AgendaAccionForm(request.POST)
        if form.is_valid():
            accion = form.save(commit=False)
            accion.user = request.user
            accion.save()
            return JsonResponse({'status': 'ok'})
        else:
            return JsonResponse({'status': 'error', 'errors': form.errors})
    return JsonResponse({'status': 'invalid_method'})

@login_required
def editar_accion_ajax(request, pk):
    accion = get_object_or_404(AgendaAccion, pk=pk, user=request.user)

    if request.method == 'POST':
        form = AgendaAccionForm(request.POST, instance=accion)
        if form.is_valid():
            form.save()
            return JsonResponse({'status': 'ok'})
        return JsonResponse({'status': 'error', 'errors': form.errors})
    
    else:
        form = AgendaAccionForm(instance=accion)
        return render(request, 'jobs/editar_modal.html', {
            'form': form,
            'accion': accion
        })

@login_required
@csrf_exempt
def eliminar_accion_ajax(request, pk):
    accion = get_object_or_404(AgendaAccion, pk=pk, user=request.user)

    if request.method == 'POST':
        accion.delete()
        return JsonResponse({'status': 'ok'})

@csrf_exempt
@login_required
def mover_accion_ajax(request, pk):
    if request.method == 'POST':
        accion = get_object_or_404(AgendaAccion, pk=pk, user=request.user)
        try:
            datos = json.loads(request.body)
            nueva_fecha_str = datos.get('nueva_fecha')

            # Convertir string a date
            nueva_fecha = datetime.strptime(nueva_fecha_str, "%Y-%m-%d").date()

            accion.fecha = nueva_fecha
            accion.save()
            return JsonResponse({'status': 'ok'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'detalle': str(e)})
    else:
        return JsonResponse({'status': 'error', 'detalle': 'Método no permitido'})