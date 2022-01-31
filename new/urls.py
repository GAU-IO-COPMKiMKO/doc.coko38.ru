from django.urls import path
from django.contrib.auth import views as auth_views
from .views import *

urlpatterns = [
    path('', main, name='main'),
    path('new', new, name='new'),
    path('<int:id_div>/<int:id_lev>/', DocsView.as_view(), name='docs'),
    path('delete/<int:id>/', delete, name='delete'),
    path('choose/', choice_docs, name='choice'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('login/', login_user, name='login'),
]