from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from .forms import EditUserForm


@login_required
def personal_information_view(request):
    """
    View to display the personal information of the logged-in user.
    """
    user = request.user
    context = {
        'user': user,
        'menu': 'personal_information',
    }
    return render(request, 'accounts/personal_information.html', context)


@login_required
def personal_information_edit_view(request):
    """
    View to edit the personal information of the logged-in user.
    """
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


def login_view(request):
    """
    View to handle user login.
    """
    from .forms import UserAuthForm

    redirect_to = request.POST.get('next', request.GET.get('next', ''))

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


def register_view(request):
    """
    View to handle user registration.
    """
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
    """
    View to handle user logout.
    """
    _next = request.GET.get('next')
    logout(request)
    return redirect(_next if _next else settings.LOGOUT_REDIRECT_URL)
