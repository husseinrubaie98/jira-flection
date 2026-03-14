from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),
    path('project/<str:project_key>/', views.project_detail, name='project_detail'),
    path('api/issues/<str:project_key>/', views.api_load_issues, name='api_load_issues'),
    path('api/subtasks/<str:issue_key>/', views.api_load_subtasks, name='api_load_subtasks'),
    path('settings/', views.settings_view, name='settings'),
]
