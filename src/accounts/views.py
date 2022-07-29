from django.shortcuts import render, redirect, get_object_or_404
from django.conf import settings
from django.http import JsonResponse, HttpResponseForbidden, HttpResponse
from django.utils.translation import ugettext as _
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils import timezone
from datetime import timedelta
from django.db.models import Q
from .models import User
from .forms import EditUserForm


@login_required
def personal_information(request):
    user = request.user
    context = {
        'user': user,
        'menu': 'personal_information',
    }
    return render(request, 'accounts/personal_information.html', context)


@login_required
def edit_personal_information(request):
    user = request.user
    if request.method == 'POST':
        form = EditUserForm(instance=user, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('personal_information'))
    else:
        form = EditUserForm(instance=user)
    context = {
        'form': form,
        'menu': 'personal_information',
    }
    return render(request, 'accounts/edit_personal_information.html', context)


def login_view(request, template_name='accounts/login.html'):
    from .forms import UserAuthForm

    redirect_to = request.POST.get('next', request.GET.get('next', ''))
    do_redirect = False

    if request.user.is_authenticated:
        if redirect_to == request.path:
            raise ValueError('Redirection loop for authenticated user detected.')
        return redirect(reverse('index'))
    elif request.method == 'POST':
        form = UserAuthForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect(reverse('index'))
    else:
        form = UserAuthForm(request)

    context = {
        'form': form,
    }
    return render(request, 'accounts/login.html', context)


def register(request, template_name='accounts/register.html'):
    from .forms import UserRegistrationForm
    if request.user.is_authenticated:
        return redirect(reverse('index'))

    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.backend = 'django.contrib.auth.backends.ModelBackend'
            login(request, user)
    else:
        form = UserRegistrationForm()

    context = {
        'form': form,
    }
    return render(request, 'accounts/register.html', context)


def logout_view(request):
    _next = request.GET.get('next')
    logout(request)
    return redirect(_next if _next else settings.LOGOUT_REDIRECT_URL)
