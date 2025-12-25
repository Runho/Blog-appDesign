from django.shortcuts import render

# Create your views here.
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from .models import BlogPost
from .forms import BlogPostForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import redirect


class HomePageView(ListView):
    model = BlogPost
    template_name = 'blogs/home.html'
    context_object_name = 'posts'
    ordering = ['-date_added']


class CreatePostView(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogs/post_form.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdatePostView(LoginRequiredMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogs/post_form.html'
    success_url = '/'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise PermissionDenied("你没有权限编辑这篇博文！")
        return obj


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('blogs:home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})


class PostDetailView(DetailView):
    model = BlogPost
    template_name = 'blogs/post_detail.html'
    context_object_name = 'post'