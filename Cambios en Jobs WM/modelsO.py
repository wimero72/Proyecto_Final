from django.db import models
from django.contrib.auth.models import User

# Oferta de empleo creada por un headhunter
class JobOffer(models.Model):
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_offers_created')
    company_name = models.CharField(max_length=200)
    title = models.CharField(max_length=200)
    description = models.TextField()
    location = models.CharField(max_length=100, blank=True)
    modality = models.CharField(
        max_length=20,
        choices=[
            ('remote', 'Remote'),
            ('onsite', 'On Site'),
            ('hybrid', 'Hybrid')
        ],
        default='onsite'
    )
    salary = models.CharField(max_length=100, blank=True)
    category = models.CharField(max_length=100, blank=True)
    requirements = models.TextField(blank=True)
    benefits = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    users = models.ManyToManyField(User, related_name='job_offers_applied', blank=True)

    def __str__(self):
        return f"{self.title} at {self.company_name}"

# Candidatura de un usuario a una oferta
CANDIDATURE_STATUS_CHOICES = [
('pendiente', 'Pendiente'),
('aceptado', 'Aceptado'),
('rechazado', 'Rechazado'),

]    
class Candidatura(models.Model):

    offer = models.ForeignKey(
        JobOffer, on_delete=models.CASCADE, related_name='candidaturas'
    )
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='candidaturas'
    )
    estado = models.CharField(
        max_length=20, choices=CANDIDATURE_STATUS_CHOICES, default='pendiente'
    )
    updated_at = models.DateTimeField(auto_now=True)

    mensaje_personalizado = models.TextField(blank=True, null=True)
    fecha_aplicacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.offer.title} ({self.estado})"
    
class StatusMessageTemplate(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="status_templates"
    )
    estado = models.CharField(
        max_length=20,
        choices= CANDIDATURE_STATUS_CHOICES,
        default='pendiente'
    )
    mensaje = models.TextField()

    class Meta:
        unique_together = ('user', 'estado')

    def __str__(self):
        return f"{self.user.username} - {self.estado}"
    





class AgendaAccion(models.Model):
    TIPOS = [
    ('entrevista', 'Entrevista'),
    ('llamada', 'Llamada'),
    ('recordatorio', 'Recordatorio'),
    ('entrega', 'Entrega'),
    ('otro', 'Otro'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='acciones')
    oferta = models.ForeignKey(JobOffer, null=True, blank=True, on_delete=models.SET_NULL, related_name='acciones')
    titulo = models.CharField(max_length=255)
    descripcion = models.TextField(blank=True)
    fecha = models.DateField()
    hora = models.TimeField()
    duracion_minutos = models.PositiveIntegerField(default=30)
    tipo = models.CharField(max_length=20, choices=TIPOS, default='otro')
    fecha_fin = models.DateTimeField(null=True, blank=True)
    finished = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['fecha']),
            models.Index(fields=['oferta']),
        ]

    def __str__(self):
        return f"{self.titulo} ({self.fecha} {self.hora})"
    
    class Postulacion(models.Model):
        user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='postulaciones')
        oferta = models.ForeignKey(JobOffer, on_delete=models.CASCADE, related_name='postulaciones')
        fecha_postulacion = models.DateTimeField(auto_now_add=True)
        mensaje = models.TextField(blank=True)

        def __str__(self):
            return f"{self.user.username} - {self.oferta.title} ({self.fecha_postulacion})"
    

