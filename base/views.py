from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, HttpResponseRedirect
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import default_storage
from .models import *
import random
from cryptography.fernet import Fernet
import io


def home(request):
    print(request.user)
    return render(request, 'home.html')

def user_register(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        first_name = request.POST['first_name']
        last_name = request.POST['last_name']
        age = request.POST['age']
        blood_groups = request.POST['blood_groups']
        gender = request.POST['gender']
        medical_note = request.POST['medical_note']
        role = request.POST['role']
        if password == password2:
            user = User.objects.create_user(username=username, password=password)
            if role in ['medical_stuff', 'doctor']:
                user_type = role
            else:
                user_type = 'normal'

            #user_type = 'normal'
            #if role in ['medical_stuff', 'doctor']:
                #user_type = role
            account_ins = Account.objects.create(user=user, user_type=user_type,first_name=first_name, last_name=last_name, age=age, blood_group=blood_groups, gender=gender, medical_note=medical_note, secret_key=''.join([random.choice('abcdefghijklmnopqrstuvwxyz') for i in range(30)]))
            user.save()
            account_ins.save()
            return redirect('home')
    return render(request, 'user_register.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        role=request.POST['role']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('upload_file')
    return render(request, 'user_login.html')

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def upload_file(request):
    context = {}
    if request.method == 'POST':
        file = request.FILES['file']
        filename = file.name
        normal_data = file.read()
        key = Fernet.generate_key()
        encrypted_data = Fernet(key).encrypt(normal_data)
        encrypted_file = ContentFile(encrypted_data, name=filename)
        file_ins = FileHandle.objects.create(user=request.user, file=encrypted_file, filename=filename, key=key)
        file_ins.save()
        context['partial_key'] = key[:10]
        
    return render(request, 'upload_file.html', context)

@login_required
def access_user_data(request):
    curr_user = request.user
    context = {}
    account_ins = Account.objects.get(user=curr_user)
    if account_ins.user_type == 'medical_stuff' or account_ins.user_type == 'doctor':
        all_accounts = Account.objects.all()
        context['all_accounts'] = all_accounts
        return render(request, 'user_data_list.html', context)
    else:
        return HttpResponse('<p>You are not a Medical Stuff or Doctor</p>')

import uuid

@login_required
def schedule_conference(request):
    if request.method == 'POST':
        participants = request.POST.getlist('participants')
        date = request.POST['date']
        time = request.POST['time']
        conference = Conference.objects.create(host=request.user, scheduled_date=date, scheduled_time=time)
        conference.participants.add(*User.objects.filter(id__in=participants))
        conference.save()
        return redirect('view_conferences')
    users = User.objects.exclude(id=request.user.id)  # Exclude the host
    return render(request, 'schedule_conference.html', {'users': users})

@login_required
def join_conference(request, meeting_id):
    conference = get_object_or_404(Conference, meeting_id=meeting_id)
    return render(request, 'join_conference.html', {'meeting_id': meeting_id, 'conference': conference})

@login_required
def view_conferences(request):
    conferences = Conference.objects.filter(participants=request.user) | Conference.objects.filter(host=request.user)
    return render(request, 'view_conferences.html', {'conferences': conferences})

@login_required
def schedule_appointment(request):
    doctors = Account.objects.filter(user_type='doctor')  # Fetch all doctors
    if request.method == 'POST':
        doctor_id = request.POST['doctor']
        date = request.POST['date']
        time = request.POST['time']
        description = request.POST['description']
        doctor = User.objects.get(pk=doctor_id)
        appointment = Appointment.objects.create(
            patient=request.user, 
            doctor=doctor, 
            date=date, 
            time=time, 
            description=description
        )
        return redirect('view_appointments')
    return render(request, 'schedule_appointment.html', {'doctors': doctors})



@login_required
def view_appointments(request):
    appointments = Appointment.objects.filter(patient=request.user)
    return render(request, 'view_appointments.html', {'appointments': appointments})

@login_required
def manage_appointments(request):
    if request.user.account.user_type == 'doctor':
        appointments = Appointment.objects.filter(doctor=request.user)
        if request.method == 'POST':
            appointment_id = request.POST.get('appointment_id')
            action = request.POST.get('action')
            appointment = get_object_or_404(Appointment, id=appointment_id)
            
            if action == 'confirm':
                appointment.status = 'Confirmed'
            elif action == 'cancel':
                appointment.status = 'Cancelled'
                return redirect('schedule_appointment')  # Redirect patient to reschedule

            appointment.save()
            return redirect('manage_appointments')

        return render(request, 'manage_appointments.html', {'appointments': appointments})
    return HttpResponse("You are not authorized to view this page.")

@login_required
def view_files(request):
    context = {}
    all_files = FileHandle.objects.all()
    list_files = []
    for file in all_files:
        list_files.append({
            'id' : file.id,
            'filename' : file.filename,
            'filepath' : file.file.url,
            'user' : file.user.username
        })
    context['all_files'] = list_files
    return render(request, 'view_files.html', context)


@login_required
def view_each_file(request, file_id):
    file_ins = FileHandle.objects.get(pk=file_id)
    key = file_ins.key

    if request.method == 'POST':
        partial_key = request.POST['partial_key']
        print("key is ",key)
        if partial_key[:8] == key[2:10]:
            key = eval(key)
            normal_data = file_ins.file.read()
            decrypted_data = Fernet(key).decrypt(normal_data)
            temp_filename = 'temp_files/{}_{}'.format(file_ins.user_id, file_ins.filename)
            path = default_storage.save(temp_filename, ContentFile(decrypted_data))
            file_url = default_storage.url(path)
            return HttpResponseRedirect(file_url)
    context = {
        'temp_key': key[2:12]
    }
    print(context['temp_key'])
    return render(request, 'view_each_file.html',context)

# @login_required
# def create_prescription(request):
#     context = {}
#     all_users = Account.objects.all()
    