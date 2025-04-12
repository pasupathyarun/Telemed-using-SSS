from django.db import models
from django.contrib.auth.models import User


class Account(models.Model):
    USER_TYPE_CHOICES = (('normal', 'normal'),('medical_stuff', 'medical_stuff'),('doctor', 'doctor'))
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=255, default='normal', choices=USER_TYPE_CHOICES)
    first_name = models.CharField(max_length=255, default='None')
    last_name = models.CharField(max_length=255, default='None')
    age = models.IntegerField()
    blood_group = models.CharField(max_length=255, default='None')
    gender = models.CharField(max_length=255, default='None')
    medical_note = models.CharField(max_length=2000, default='None')
    secret_key = models.CharField(max_length = 50, default='expectropatronum')
    def __str__(self):
        return f'{self.user.username} - {self.first_name} - {self.last_name}'

class FileHandle(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='uploads')
    filename = models.CharField(max_length=2000, default='None')
    key = models.CharField(max_length=255, default='None')
    
    def __str__(self):
        return self.filename
class Appointment(models.Model):
    patient = models.ForeignKey(User, related_name='appointments', on_delete=models.CASCADE)
    doctor = models.ForeignKey(User, related_name='doctor_appointments', on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Confirmed', 'Confirmed'), ('Cancelled', 'Cancelled')], default='Pending')

    def __str__(self):
        return f"Appointment with {self.doctor.username} on {self.date} at {self.time}"

class Prescription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    details = models.CharField(max_length=2000, default='None')


    def __str__(self):
        return f'{self.user.username}'
    
import uuid

class Conference(models.Model):
    host = models.ForeignKey(User, related_name='hosted_conferences', on_delete=models.CASCADE)
    participants = models.ManyToManyField(User, related_name='conferences')
    meeting_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    scheduled_date = models.DateField()
    scheduled_time = models.TimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Meeting {self.meeting_id} hosted by {self.host.username}"
