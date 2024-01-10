from django.urls import path
from . import views

app_name = 'imapp'
urlpatterns = [
    # ex: /imapp/
    path('', views.IndexView.as_view(), name='index'),
    # ex: /imapp/register, /imapp/deregister ...
    path('register/', views.register.as_view(), name='register'),
    path('log/', views.LogView.as_view(), name='log'),
    path('sclog/', views.scLogView.as_view(), name='sclog'),
    # ex: /imapp/log/D01/
    path('log/<str:sam_site>/', views.loglog, name='loglog'),
    # unregister
    path('unregister/index/<int:mode_id>/', views.UnregisterIndexView.as_view(), name='unregister_index'),
    path('unregister/confirm/<int:mode_id>/', views.UnregisterConfirmView.as_view(), name='unregister_confirm'),
    path('unregister/run/<int:mode_id>', views.run_unregister, name='unregister_run'),
]
