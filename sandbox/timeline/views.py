from django.shortcuts import render

# Create your views here.

@login_required
def home_view(request):
    """Display the home feed."""
    if request.method == 'POST':
        form = PostForm(request.POST)
        if form.is_valid():
            new_post = form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            return redirect('home')
    else:
        form = PostForm()
    following_profiles = request.user.profile.following.all()
    posts = Post.objects.filter(author__profile__in=following_profiles).order_by('-created_at')
    context = {
        'form': form,
        'posts': posts,
    }
    return render(request, 'home.html', context)