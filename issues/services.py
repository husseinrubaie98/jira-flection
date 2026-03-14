"""JIRA API service layer."""

import requests
from requests.auth import HTTPBasicAuth
from .models import JiraSetting


class JiraAPIError(Exception):
    """Raised when JIRA API calls fail."""
    pass


class JiraService:
    """Handles all communication with the JIRA REST API."""

    def __init__(self):
        self.base_url = JiraSetting.get('jira_url', '').rstrip('/')
        self.email = JiraSetting.get('jira_email', '')
        self.api_token = JiraSetting.get('jira_api_token', '')

    def _is_configured(self):
        """Check if JIRA settings are properly configured."""
        return bool(self.base_url and self.email and self.api_token)

    def _get_auth(self):
        """Get HTTP Basic Auth for JIRA Cloud."""
        return HTTPBasicAuth(self.email, self.api_token)

    def _get_headers(self):
        return {
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }

    def _make_request(self, endpoint, method='GET', params=None):
        """Make an authenticated request to the JIRA API."""
        if not self._is_configured():
            raise JiraAPIError(
                'JIRA is not configured. Please go to Settings and provide '
                'your JIRA URL, email, and API token.'
            )

        # Jira v3 migration: Updated base path
        url = f'{self.base_url}/rest/api/3/{endpoint}'
        try:
            response = requests.request(
                method,
                url,
                headers=self._get_headers(),
                auth=self._get_auth(),
                params=params,
                timeout=30,
            )
            response.raise_for_status()
            return response.json() if response.content else {}
        except requests.exceptions.ConnectionError:
            raise JiraAPIError(
                f'Could not connect to JIRA at {self.base_url}. '
                'Please check your JIRA URL in Settings.'
            )
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 401:
                raise JiraAPIError(
                    'Authentication failed. Please check your email and API token in Settings.'
                )
            elif e.response.status_code == 403:
                raise JiraAPIError(
                    'Access forbidden. Your API token may not have sufficient permissions.'
                )
            elif e.response.status_code == 404:
                raise JiraAPIError(
                    'Resource not found. Please check your JIRA URL in Settings.'
                )
            raise JiraAPIError(f'JIRA API error: {e.response.status_code} - {e.response.text}')
        except requests.exceptions.Timeout:
            raise JiraAPIError('Request to JIRA timed out. Please try again.')
        except Exception as e:
            raise JiraAPIError(f'Unexpected error: {str(e)}')

    def _extract_adf_text(self, node):
        """Extract plain text from Atlassian Document Format (ADF) JSON."""
        if not node:
            return ""
        if isinstance(node, str):
            return node
        if isinstance(node, list):
            return ' '.join(self._extract_adf_text(child) for child in node)
        if isinstance(node, dict):
            if node.get('type') == 'text' and 'text' in node:
                return node['text']
            
            content = ""
            if 'content' in node:
                content = self._extract_adf_text(node['content'])
            
            # Add newline for block elements
            if node.get('type') in ['paragraph', 'heading', 'listItem', 'codeBlock'] and content:
                content += "\n"
            return content
        return ""

    def get_projects(self):
        """Fetch all accessible projects from JIRA using v3 project search."""
        all_projects = []
        start_at = 0
        max_results = 50

        while True:
            data = self._make_request('project/search', params={
                'startAt': start_at,
                'maxResults': max_results
            })
            
            values = data.get('values', [])
            for p in values:
                all_projects.append({
                    'key': p.get('key', ''),
                    'name': p.get('name', ''),
                    'id': p.get('id', ''),
                    'avatar': p.get('avatarUrls', {}).get('48x48', ''),
                })
            
            if data.get('isLast', True):
                break
            start_at += len(values)

        return sorted(all_projects, key=lambda x: x['name'])

    def get_issues(self, project_key, next_page_token=None):
        """Fetch a page of issues for a given project using v3 search."""
        params = {
            'jql': f'project="{project_key}"',
            'fields': 'summary,description,issuetype,status,priority',
            'maxResults': 50
        }
        if next_page_token:
            params['nextPageToken'] = next_page_token

        data = self._make_request('search/jql', params=params)

        issues = []
        for issue in data.get('issues', []):
            fields = issue.get('fields', {})
            description = fields.get('description', '')
            if isinstance(description, dict):
                description = self._extract_adf_text(description)
            issues.append({
                'key': issue.get('key', ''),
                'summary': fields.get('summary', ''),
                'description': description or '',
                'issue_type': fields.get('issuetype', {}).get('name', ''),
                'status': fields.get('status', {}).get('name', ''),
                'priority': fields.get('priority', {}).get('name', '') if fields.get('priority') else '',
            })

        return {
            'issues': issues,
            'nextPageToken': data.get('nextPageToken')
        }

    def get_subtasks(self, issue_key):
        """Fetch subtasks for a given issue using v3 search."""
        # Note: subtasks are usually fewer, but using search for consistency
        data = self._make_request('search/jql', params={
            'jql': f'parent="{issue_key}"',
            'fields': 'summary,description,issuetype,status,priority'
        })

        subtasks = []
        for issue in data.get('issues', []):
            fields = issue.get('fields', {})
            description = fields.get('description', '')
            if isinstance(description, dict):
                description = self._extract_adf_text(description)
            subtasks.append({
                'key': issue.get('key', ''),
                'summary': fields.get('summary', ''),
                'description': description or '',
                'issue_type': fields.get('issuetype', {}).get('name', ''),
                'status': fields.get('status', {}).get('name', ''),
                'priority': fields.get('priority', {}).get('name', '') if fields.get('priority') else '',
            })

        return subtasks

    def get_issue(self, issue_key):
        """Fetch a single issue by key using v3 API."""
        data = self._make_request(f'issue/{issue_key}')
        fields = data.get('fields', {})
        description = fields.get('description', '')
        if isinstance(description, dict):
            description = self._extract_adf_text(description)
        return {
            'key': data.get('key', ''),
            'id': data.get('id', ''),
            'summary': fields.get('summary', ''),
            'description': description or '',
            'issue_type': fields.get('issuetype', {}).get('name', ''),
            'status': fields.get('status', {}).get('name', ''),
            'priority': fields.get('priority', {}).get('name', '') if fields.get('priority') else '',
            'link': f"{self.base_url}/browse/{data.get('key', '')}"
        }
