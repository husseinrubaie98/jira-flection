import json
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from .models import JiraSetting
from .services import JiraService, JiraAPIError


def projects(request):
    """Home page - list all JIRA projects."""
    jira = JiraService()
    project_list = []
    error = None

    if jira._is_configured():
        try:
            project_list = jira.get_projects()
        except JiraAPIError as e:
            error = str(e)
    else:
        error = (
            'JIRA is not configured yet. Please go to '
            '<a href="/settings/">Settings</a> to set up your connection.'
        )

    return render(request, 'issues/projects.html', {
        'projects': project_list,
        'error': error,
    })


def project_detail(request, project_key):
    """Project detail page with 'Load Issues' button."""
    return render(request, 'issues/project_detail.html', {
        'project_key': project_key,
    })


def api_load_issues(request, project_key):
    """API endpoint: load issues for a project (called via AJAX)."""
    jira = JiraService()
    next_page_token = request.GET.get('nextPageToken')
    try:
        data = jira.get_issues(project_key, next_page_token)
        return JsonResponse({
            'success': True, 
            'issues': data['issues'], 
            'nextPageToken': data['nextPageToken']
        })
    except JiraAPIError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def api_load_subtasks(request, issue_key):
    """API endpoint: load subtasks for an issue (called via AJAX)."""
    jira = JiraService()
    try:
        subtask_list = jira.get_subtasks(issue_key)
        return JsonResponse({'success': True, 'subtasks': subtask_list})
    except JiraAPIError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def settings_view(request):
    """Settings page to configure JIRA connection."""
    if request.method == 'POST':
        jira_url = request.POST.get('jira_url', '').strip()
        jira_email = request.POST.get('jira_email', '').strip()
        jira_api_token = request.POST.get('jira_api_token', '').strip()

        JiraSetting.set('jira_url', jira_url)
        JiraSetting.set('jira_email', jira_email)
        if jira_api_token:
            JiraSetting.set('jira_api_token', jira_api_token)

        messages.success(request, 'Settings saved successfully!')
        return redirect('settings')

    context = {
        'jira_url': JiraSetting.get('jira_url', ''),
        'jira_email': JiraSetting.get('jira_email', ''),
        'jira_api_token': JiraSetting.get('jira_api_token', ''),
    }
    return render(request, 'issues/settings.html', context)

def api_search_issue(request):
    """API endpoint: search for a single issue and return it in the issues array format."""
    jira = JiraService()
    issue_key = request.GET.get('issue_key', '').strip()
    
    if not issue_key:
        return JsonResponse({'success': False, 'error': 'No issue key provided'}, status=400)

    try:
        issue = jira.get_issue(issue_key)
        # Wrap the single issue in a list to match the UI's table expectation
        return JsonResponse({'success': True, 'issues': [issue], 'nextPageToken': None})
    except JiraAPIError as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

def issue_search(request):
    """Search for an issue by key from a form submission."""
    issue_key = request.GET.get('issue_key', '').strip()
    if not issue_key:
        return redirect('projects')
    return redirect('issue_detail_view', issue_key=issue_key)

def issue_detail_view(request, issue_key):
    """View details of a single issue."""
    jira = JiraService()
    issue = None
    error = None

    if jira._is_configured():
        try:
            issue = jira.get_issue(issue_key)
        except JiraAPIError as e:
            error = str(e)
    else:
        error = (
            'JIRA is not configured yet. Please go to '
            '<a href="/settings/">Settings</a> to set up your connection.'
        )

    return render(request, 'issues/issue_detail.html', {
        'issue_key': issue_key,
        'issue': issue,
        'error': error,
    })
