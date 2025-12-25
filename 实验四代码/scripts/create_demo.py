import os
import sys
import django

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blog.settings')
django.setup()

from django.contrib.auth import get_user_model
from blogs.models import BlogPost

User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    print('superuser created: admin / adminpass')
else:
    print('superuser already exists')

u = User.objects.get(username='admin')
if BlogPost.objects.count() == 0:
    BlogPost.objects.create(title='Hello World', text='This is the first post.', author=u)
    BlogPost.objects.create(title='Second Post', text='Another short post.', author=u)
    print('created 2 demo posts')
else:
    print('posts already exist:', BlogPost.objects.count())
