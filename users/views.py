import csv

from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import User
import re


# Create your views here.
def signup(request):
    context = {}
    # whatever
    if request.method == 'POST':
        data = request.POST.copy()
        email = data.get('email')
        password = data.get('password')
        confirmpassword = data.get('confirmpassword')
        Emails = User.objects.all().values_list('email', flat=True)
        EMAIL_REGEX = re.compile(r"[^ @]+@[^ @]+\.[^ @]+")

        if not EMAIL_REGEX.match(email):
            context['error'] = "Invalid Email"
        elif password.strip() == confirmpassword.strip() and password.strip() != "" and email.strip() != "" and email not in Emails:
            user_object = User.objects.create(email=email, password=password)
            user_object.save()
            return HttpResponseRedirect('/accounts/login/')
        elif email in Emails:
            context['error'] = "Email is already taken"
        elif password.strip() != confirmpassword.strip():
            context['error'] = "Password Mismatch"
        print(email, password, confirmpassword)

    return render(request, 'SignUp.html', context)


def login(request):
    context = {}
    if request.method == 'POST':
        data = request.POST.copy()
        email = data.get('email')
        password = data.get('password')
        Emails = User.objects.all().values_list('email', flat=True)
        if email in Emails and password == User.objects.filter(email=email)[0].password:
            return HttpResponseRedirect('/accounts/login/')
        else:
            context['error'] = "Invalid Email or Password"
        print(email, password)
    return render(request, 'login.html', context)

@permission_required('admin.can_add_log_entry')
def export_users_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="users.csv"'

    writer = csv.writer(response)
    emails = User.objects.all().values_list('email', flat=True)
    for email in emails:
        writer.writerow([email])

    return response
