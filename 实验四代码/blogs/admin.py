from django.contrib import admin
from .models import BlogPost


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_added')
    list_filter = ('date_added', 'author')
    search_fields = ('title', 'text')
from django.contrib import admin

# Register your models here.
