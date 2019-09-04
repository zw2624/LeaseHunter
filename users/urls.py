from django.urls import path

from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.index, name='index'),
    path('home/', views.update_profile, name='profile'),
    path('signup/', views.SignUp.as_view(), name='signup'),
    path('add_house/', views.add_house, name='add'),
    path('save_house/', views.save_house, name='save'),
    path('delete/', views.delete, name='delete'),
    path('change/', views.change, name='change'),
path('add_comment/', views.add_comment, name='add_comment'),
path('save_comment/', views.save_comment, name='save_comment'),
path('like/', views.like, name='like'),
path('unlike/', views.unlike, name='unlike'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)