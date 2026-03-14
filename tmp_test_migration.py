import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# Mock Django models before importing services
sys.modules['django'] = MagicMock()
sys.modules['django.db'] = MagicMock()
sys.modules['django.conf'] = MagicMock()

class JiraSettingMock:
    @staticmethod
    def get(key, default=''):
        settings = {
            'jira_url': 'https://example.atlassian.net',
            'jira_email': 'test@example.com',
            'jira_api_token': 'fake-token'
        }
        return settings.get(key, default)

# Import the service with mocked dependencies
with patch('issues.models.JiraSetting', JiraSettingMock):
    from issues.services import JiraService, JiraAPIError

class TestJiraMigration(unittest.TestCase):
    def setUp(self):
        self.service = JiraService()

    @patch('requests.request')
    def test_get_projects_v3(self, mock_request):
        # Mock V3 project search response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"values": [{"key": "PROJ", "name": "Project", "id": "10000"}], "isLast": true}'
        mock_response.json.return_value = {
            "values": [{"key": "PROJ", "name": "Project", "id": "10000"}],
            "isLast": True
        }
        mock_request.return_value = mock_response

        projects = self.service.get_projects()
        
        self.assertEqual(len(projects), 1)
        self.assertEqual(projects[0]['key'], 'PROJ')
        # Verify it used the V3 endpoint
        args, kwargs = mock_request.call_args
        self.assertIn('/rest/api/3/project/search', args[1])

    @patch('requests.request')
    def test_get_issues_v3(self, mock_request):
        # Mock V3 search/jql response
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = b'{"issues": [{"key": "PROJ-1", "fields": {"summary": "Test"}}, {"key": "PROJ-2", "fields": {"summary": "Test 2"}}], "nextPageToken": null}'
        mock_response.json.return_value = {
            "issues": [
                {"key": "PROJ-1", "fields": {"summary": "Test"}},
                {"key": "PROJ-2", "fields": {"summary": "Test 2"}}
            ],
            "nextPageToken": None
        }
        mock_request.return_value = mock_response

        issues = self.service.get_issues('PROJ')
        
        self.assertEqual(len(issues), 2)
        self.assertEqual(issues[0]['key'], 'PROJ-1')
        # Verify it used the V3 search/jql endpoint
        args, kwargs = mock_request.call_args
        self.assertIn('/rest/api/3/search/jql', args[1])
        self.assertEqual(kwargs['params']['jql'], 'project="PROJ"')

if __name__ == '__main__':
    unittest.main()
