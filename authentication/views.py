from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User
from django.contrib.auth import login, logout
from django.urls import reverse
from helpers.decorators import auth_user_should_not_access
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from .utils import generate_token
from django.core.mail import EmailMessage
from django.conf import settings
from django.db import IntegrityError, transaction

from .forms import LoginForm, RegistrationForm


def add_form_errors_to_messages(request, form):
    seen_messages = set()
    for errors in form.errors.values():
        for error in errors:
            if error not in seen_messages:
                messages.add_message(request, messages.ERROR, error)
                seen_messages.add(error)


def send_activation_email(user, request):
    current_site = get_current_site(request)
    email_subject = 'Activate your account'
    email_body = render_to_string('authentication/activate.html', {
        'user': user,
        'domain': current_site,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': generate_token.make_token(user)
    })

    email = EmailMessage(subject=email_subject, body=email_body,
                         from_email=settings.EMAIL_FROM_USER,
                         to=[user.email]
                         )

    if not settings.TESTING:
        transaction.on_commit(
            lambda: email.send(fail_silently=settings.DEBUG)
        )

@auth_user_should_not_access
def register(request):
    form = RegistrationForm(request.POST or None)

    if request.method == "POST":
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    send_activation_email(user, request)
            except IntegrityError:
                if User.objects.filter(username=form.cleaned_data["username"]).exists():
                    form.add_error("username", "Username is taken, choose another one")
                if User.objects.filter(email=form.cleaned_data["email"]).exists():
                    form.add_error("email", "Email is taken, choose another one")
            else:
                messages.add_message(request, messages.SUCCESS, 'We sent you an email to verify your account')
                return redirect('login')

        add_form_errors_to_messages(request, form)
        return render(
            request,
            'authentication/register.html',
            {'form': form},
            status=409,
        )

    return render(request, 'authentication/register.html', {'form': form})
   


@auth_user_should_not_access
def login_user(request):
    form = LoginForm(request.POST or None, request=request)

    if request.method == 'POST':
        if form.is_valid():
            user = form.get_user()
            login(request, user)

            messages.add_message(request, messages.SUCCESS,
                                 f'Welcome {user.username}')

            return redirect(reverse('home'))

        add_form_errors_to_messages(request, form)
        return render(
            request,
            'authentication/login.html',
            {'form': form},
            status=401,
        )

    return render(request, 'authentication/login.html', {'form': form})


def logout_user(request):

    logout(request)

    messages.add_message(request, messages.SUCCESS,
                         'Successfully logged out')

    return redirect(reverse('login'))


def activate_user(request, uidb64, token):

    try:
        uid = force_str(urlsafe_base64_decode(uidb64))

        user = User.objects.get(pk=uid)

    except Exception:
        user = None

    if user and generate_token.check_token(user, token):
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])

        messages.add_message(request, messages.SUCCESS,
                             'Email verified, you can now login')
        return redirect(reverse('login'))

    return render(request, 'authentication/activate-failed.html', {"user": user})
