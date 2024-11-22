# users/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from .forms import UserRegisterForm, UserLoginForm
from django.contrib.auth.decorators import login_required
from .models import User

def register_view(request):
    """Handle user registration."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('home')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

def login_view(request):
    """Handle user login."""
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        form = UserLoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {user.username}!")
                return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = UserLoginForm()
    return render(request, 'users/login.html', {'form': form})

@login_required
def logout_view(request):
    """Handle user logout."""
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect('login')

@login_required
def profile_view(request, username):
    """Display a user's profile."""
    profile_user = get_object_or_404(User, username=username)
    profile = profile_user.profile
    is_following = profile.followers.filter(id=request.user.profile.id).exists()
    context = {
        'profile_user': profile_user,
        'profile': profile,
        'is_following': is_following,
    }
    return render(request, 'users/profile.html', context)

@login_required
def follow_view(request, username):
    """Follow a user."""
    target_user = get_object_or_404(User, username=username)
    if request.user == target_user:
        messages.error(request, "You cannot follow yourself.")
    else:
        request.user.profile.following.add(target_user.profile)
        messages.success(request, f"You are now following {target_user.username}.")
    return redirect('profile', username=username)

@login_required
def unfollow_view(request, username):
    """Unfollow a user."""
    target_user = get_object_or_404(User, username=username)
    request.user.profile.following.remove(target_user.profile)
    messages.info(request, f"You have unfollowed {target_user.username}.")
    return redirect('profile', username=username)