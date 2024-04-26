from helpers.api_caller import APICaller
from helpers.api_caller_jira import APICallerJIRA
import helpers.utils as utils


class APICallerBB (APICaller):
    ''' Implement calls to BB Rest API
    '''

    URL_PR_LIST     = '/rest/api/1.0/projects/{}/repos/{}/pull-requests'
    URL_PR_CHANGE   = '/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/changes'
    URL_PR_COMMENT  = '/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/comments'
    URL_COMMIT_PR   = '/rest/api/1.0/projects/{}/repos/{}/commits/{}/pull-requests'
    URL_UNWATCH_PR  = '/rest/api/latest/projects/{}/repos/{}/pull-requests/{}/watch'
    CONFIG_SECTION  = "BB-API"


    def get_header(self):
        return f'{utils.base64_decode(self._config.id)}:{utils.base64_decode(self._config.key)}'
    

    def get_pull_requests(self, project_key, repository_slug, target_branch='any', state='OPEN'):
        json_body = {
            'state': state
        }
        if target_branch != 'any':
            json_body['at'] = target_branch

        return self.do_get(self.URL_PR_LIST.format(project_key, repository_slug), json_body)

    
    def get_pr_change (self, project_key, repository_slug, pr_id):
        return self.do_get(self.URL_PR_CHANGE.format(project_key,repository_slug, pr_id), None)

    
    def post_pr_comment(self, project_key, repository_slug, pr_id, comment:str):
        json_body = {
            'text': comment
        }
        return self.do_post(self.URL_PR_COMMENT.format(project_key,repository_slug, pr_id), json_body)


    def get_commit_pr(self, project_key, repository_slug, commit_id):
        return self.do_get(self.URL_COMMIT_PR.format(project_key, repository_slug, commit_id), None)

    
    def unwatch_pr(self, project_key, repository_slug, pr_id):
        return self.do_delete(self.URL_UNWATCH_PR.format(project_key,repository_slug, pr_id))