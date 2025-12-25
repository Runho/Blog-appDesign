from django.urls import path
from .views import HomePageView, CreatePostView, UpdatePostView, register, PostDetailView

app_name = 'blogs'

urlpatterns = [
    path('', HomePageView.as_view(), name='home'),
    path('post/new/', CreatePostView.as_view(), name='post-create'),
    path('post/<int:pk>/edit/', UpdatePostView.as_view(), name='post-update'),
    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('accounts/register/', register, name='register'),
]
