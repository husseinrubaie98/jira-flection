from django.urls import path
from . import views

urlpatterns = [
    path('', views.projects, name='projects'),
    path('project/<str:project_key>/', views.project_detail, name='project_detail'),
    path('api/issues/<str:project_key>/', views.api_load_issues, name='api_load_issues'),
    path('api/subtasks/<str:issue_key>/', views.api_load_subtasks, name='api_load_subtasks'),
    path('api/issue/search/', views.api_search_issue, name='api_search_issue'),
    path('settings/', views.settings_view, name='settings'),
    path('issue/search/', views.issue_search, name='issue_search'),
    path('issue/<str:issue_key>/', views.issue_detail_view, name='issue_detail_view'),
]
