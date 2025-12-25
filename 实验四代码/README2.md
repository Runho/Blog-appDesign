# README2 — 项目新增代码与完整目录说明

本文件将把在本项目中新增的重要代码逐个列出（包含文件路径、代码内容与功能说明），方便审阅、复现与二次开发。

说明：这是对 `README.md` 的补充（更偏向代码级），覆盖 `blogs` 应用的模型、表单、视图、路由、模板片段、静态资源，以及对 `Blog/settings.py` 的关键配置变更与 `scripts/create_demo.py`。

---

目录索引（新增/修改的关键文件）

- `Blog/settings.py`（部分片段）
- `Blog/urls.py`（项目路由）
- `blogs/models.py`
- `blogs/forms.py`
- `blogs/views.py`
- `blogs/urls.py`
- `blogs/admin.py`
- `blogs/templates/blogs/home.html`
- `blogs/templates/blogs/post_form.html`
- `blogs/templates/blogs/post_detail.html`
- `templates/base.html`（项目级基模版）
- `templates/registration/login.html` 与 `templates/registration/register.html`
- `static/css/style.css`（核心样式片段）
- `static/js/site.js`（汉堡菜单脚本）
- `scripts/create_demo.py`

---

1) `Blog/settings.py`（关键变更片段）

```python
# 添加 apps
INSTALLED_APPS += [
    'blogs',
]

# 项目级模板目录
TEMPLATES[0]['DIRS'] = [BASE_DIR / 'templates']

# 开发时添加项目静态目录
STATICFILES_DIRS = [BASE_DIR / 'static']

# 登录相关
LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
```

用途：保证开发服务器能加载项目级模板和静态文件，并定义登录重定向行为。

---

2) `Blog/urls.py`（项目路由）

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('blogs.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
]
```

说明：将 `blogs` 应用挂载到根路径，并启用 Django 自带的认证路由（login/logout/password）。

---

3) `blogs/models.py`

```python
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()

class BlogPost(models.Model):
    title = models.CharField(max_length=200)
    text = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-date_added']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('blogs:post-detail', args=[self.pk])
```

说明：博客主要实体，包含作者引用并默认按时间倒序展示。

---

4) `blogs/forms.py`

```python
from django import forms
from .models import BlogPost

class BlogPostForm(forms.ModelForm):
    class Meta:
        model = BlogPost
        fields = ['title', 'text']

```

用途：用于创建与编辑文章的表单。

---

5) `blogs/views.py`

```python
from django.shortcuts import redirect
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.core.exceptions import PermissionDenied

from .models import BlogPost
from .forms import BlogPostForm

class HomePageView(ListView):
    model = BlogPost
    template_name = 'blogs/home.html'
    context_object_name = 'posts'
    paginate_by = 10


class CreatePostView(LoginRequiredMixin, CreateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogs/post_form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)


class UpdatePostView(LoginRequiredMixin, UpdateView):
    model = BlogPost
    form_class = BlogPostForm
    template_name = 'blogs/post_form.html'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        if obj.author != self.request.user:
            raise PermissionDenied
        return obj


class PostDetailView(DetailView):
    model = BlogPost
    template_name = 'blogs/post_detail.html'


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('/')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
```

说明：列表/创建/编辑/详情视图与注册视图的实现；编辑视图包含作者校验以保护权限。

---

6) `blogs/urls.py`

```python
from django.urls import path
from . import views

app_name = 'blogs'

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('post/new/', views.CreatePostView.as_view(), name='post-create'),
    path('post/<int:pk>/edit/', views.UpdatePostView.as_view(), name='post-update'),
    path('post/<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),
    path('accounts/register/', views.register, name='register'),
]
```

说明：应用级路由，命名空间为 `blogs`，便于反向解析。

---

7) `blogs/admin.py`

```python
from django.contrib import admin
from .models import BlogPost

@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'date_added')
    search_fields = ('title', 'text')
    list_filter = ('date_added', 'author')
```

作用：在 Django 管理后台方便管理博文。

---

8) 关键模板片段（`templates/base.html`）

```html
{% load static %}
<!doctype html>
<html lang="zh-CN">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <link rel="stylesheet" href="{% static 'css/style.css' %}">
  <title>{% block title %}My Blog{% endblock %}</title>
</head>
<body>
  <header class="site-header">
    <nav class="nav">
      <a class="brand" href="/">My Blog</a>
      <button id="navToggle" class="nav-toggle">☰</button>
      <ul id="navMenu" class="nav-menu">
        <li><a href="/">Home</a></li>
        {% if user.is_authenticated %}
          <li><a href="/post/new/">Create new post</a></li>
          <li><a href="{% url 'logout' %}">Logout</a></li>
        {% else %}
          <li><a href="{% url 'login' %}">Login</a></li>
          <li><a href="{% url 'blogs:register' %}">Register</a></li>
        {% endif %}
      </ul>
    </nav>
  </header>

  <main>
    {% block content %}{% endblock %}
  </main>

  <script src="{% static 'js/site.js' %}"></script>
</body>
</html>
```

说明：基础布局、导航与静态资源引用。

---

9) `blogs/templates/blogs/home.html`

```html
{% extends 'base.html' %}
{% block title %}Home - My Blog{% endblock %}
{% block content %}
  <section class="post-list">
    {% for post in posts %}
      <article class="post-card">
        <h2>{{ post.title }}</h2>
        <p class="meta">By {{ post.author }} — {{ post.date_added|date:"Y-m-d H:i" }}</p>
        <p class="excerpt">{{ post.text|truncatechars:200 }}</p>
        <a class="btn" href="{% url 'blogs:post-detail' post.pk %}" target="_blank">Read</a>
        {% if user == post.author %}
          <a class="btn muted" href="{% url 'blogs:post-update' post.pk %}">Edit</a>
        {% endif %}
      </article>
    {% empty %}
      <p>No posts yet.</p>
    {% endfor %}
  </section>
  {% if is_paginated %}
    <!-- pagination controls -->
  {% endif %}
{% endblock %}
```

说明：首页列出文章卡片，`Read` 在新标签打开详情页。

---

10) `blogs/templates/blogs/post_form.html`

```html
{% extends 'base.html' %}
{% block content %}
  <h1>{% if form.instance.pk %}Edit{% else %}New{% endif %} Post</h1>
  <form method="post">{% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Save</button>
  </form>
{% endblock %}
```

---

11) `blogs/templates/blogs/post_detail.html`

```html
{% extends 'base.html' %}
{% block content %}
  <article class="post-detail">
    <h1>{{ object.title }}</h1>
    <p class="meta">By {{ object.author }} — {{ object.date_added|date:"Y-m-d H:i" }}</p>
    <div class="content">{{ object.text|linebreaks }}</div>
    {% if user == object.author %}
      <a href="{% url 'blogs:post-update' object.pk %}">Edit</a>
    {% endif %}
  </article>
{% endblock %}
```

---

12) `templates/registration/login.html`（简化）

```html
{% extends 'base.html' %}
{% block content %}
  <h1>Login</h1>
  <form method="post">{% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Login</button>
  </form>
{% endblock %}
```

`templates/registration/register.html` 类似，使用 `UserCreationForm`。

---

13) 静态脚本 `static/js/site.js`

```javascript
document.addEventListener('DOMContentLoaded', function () {
  var btn = document.getElementById('navToggle');
  var menu = document.getElementById('navMenu');
  if (btn && menu) {
    btn.addEventListener('click', function () {
      menu.classList.toggle('open');
    });
    document.addEventListener('click', function (e) {
      if (!menu.contains(e.target) && e.target !== btn) {
        menu.classList.remove('open');
      }
    });
  }
});
```

用途：控制移动端汉堡菜单展开与收起。

---

14) 样式片段 `static/css/style.css`（关键变量与结构）

```css
:root{ --brand:#2b6cb0; --muted:#6b7280; --bg:#f7fafc }
body{ font-family: system-ui, -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial; background:var(--bg); color:#111 }
.site-header{ background:#fff; border-bottom:1px solid #e6e6e6 }
.nav{ display:flex; align-items:center; justify-content:space-between; padding:0.5rem 1rem }
.nav-menu{ display:flex; gap:0.5rem; list-style:none }
.nav-toggle{ display:none }
.post-list{ display:grid; gap:1rem; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); padding:1rem }
.post-card{ background:#fff; padding:1rem; border-radius:6px; box-shadow:0 1px 3px rgba(0,0,0,0.05) }
.btn{ display:inline-block; padding:0.4rem 0.7rem; background:var(--brand); color:#fff; border-radius:4px; text-decoration:none }
@media (max-width:720px){ .nav-menu{ display:none } .nav-menu.open{ display:flex; flex-direction:column } .nav-toggle{ display:inline-block } }
```

说明：主要样式确保响应式与卡片化展示。

---

15) `scripts/create_demo.py`

```python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blog.settings')
django.setup()

from django.contrib.auth import get_user_model
from blogs.models import BlogPost

User = get_user_model()

if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'adminpass')
    print('superuser created: admin / adminpass')

if BlogPost.objects.count() == 0:
    admin = User.objects.get(username='admin')
    BlogPost.objects.create(title='Hello World', text='This is the first demo post.', author=admin)
    BlogPost.objects.create(title='Second Post', text='Another demo post.', author=admin)
    print('created 2 demo posts')

```

注意：示例密码仅用于本地开发，切勿在生产环境中使用。

---

附注 — 变更要点与验证

- 确保已运行 `python manage.py migrate` 完成迁移。
- 若在浏览器看不到 CSS 更改，先清除缓存或按 `Ctrl+F5` 强制刷新。开发时也可在 `base.html` 的静态链接后附带时间戳参数以防缓存。

---

如果你希望我：
- 把 `README2.md` 中的代码逐一写回对应文件（即覆盖或创建这些文件），我可以继续替你应用这些改动并运行一次本地验证；
- 或者只需我把 README2 精简为更便于阅读的版本，也请告知你要的侧重点（例如部署、Docker、CI、测试）。

---

（结束）
