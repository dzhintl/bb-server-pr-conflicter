import base64
from configparser import SafeConfigParser
import json
import logging
import requests
from models.credential import Credential
import helpers.utils as utils


class BBAPICaller:
    ''' Implement calls to BB Rest API
    '''

    class Config:
        KEY_URL      = 'BB_URL'

        url: str
        header_key: str

        def __init__(self, url, credential:Credential) -> None:
            self.url        = url
            header = f'{credential.get_username()}:{credential.get_password()}'
            self.header_key = base64.b64encode(bytes(header, 'utf-8')).decode('ascii')


    _config: Config
    _logger = logging.getLogger(__name__)

    url_pullrequest   = '/rest/api/1.0/projects/{}/repos/{}/pull-requests'
    url_pr_change     = '/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/changes'
    url_pr_comments   = '/rest/api/1.0/projects/{}/repos/{}/pull-requests/{}/comments'
    url_commit_pr     = '/rest/api/1.0/projects/{}/repos/{}/commits/{}/pull-requests'

    def __init__(self, config_file, section) -> None:
        config_parser = SafeConfigParser()
        config_parser.read(config_file)

        if config_parser.has_option(section, BBAPICaller.Config.KEY_URL):
            url = config_parser.get(section, BBAPICaller.Config.KEY_URL)
            self._config = BBAPICaller.Config(url, Credential(config_file, section))
        else:
            raise Exception ('Exception while setting up config')
    

    def construct_url(self, url:str, *args):
        return f'{self._config.url}{url.format(*args[0])}'


    def construct_header(self):
        return {'Authorization': f'Basic {self._config.header_key}'}


    def do_get(self, url, params=None, *args):
        url = self.construct_url(url, args[0])

        self._logger.info ('Initiating GET call to: {}'.format(url))
        
        response = requests.get(url, params=params, headers=self.construct_header()).json()
        
        self._logger.debug (f'GET from [{url}] receiving response:{response}')
        
        return utils.json_to_object(json.dumps(response))


    def do_post(self, url, json_body, *args):
        url = self.construct_url(url, args[0])

        self._logger.info ('Initiating POST call to: {}'.format(url))
        
        response = requests.post(url, json=json_body, headers=self.construct_header()).json()
        
        self._logger.debug (f'POST to [{url}] receiving response:{response}')
        
        return utils.json_to_object(json.dumps(response))


    def get_pull_requests(self, project_key, repository_slug, target_branch, state='OPEN'):
        params = {
            'at': target_branch,
            'state': state
        }
        return self.do_get(self.url_pullrequest, params, (project_key,repository_slug))

    
    def get_pr_change (self, project_key, repository_slug, pr_id):
        return self.do_get(self.url_pr_change, None, (project_key,repository_slug, pr_id))

    
    def post_pr_comment(self, project_key, repository_slug, pr_id, comment:str):
        json_body = {
            'text': comment
        }
        return self.do_post(self.url_pr_comments, json_body, (project_key,repository_slug, pr_id))

    
    def get_commit_pr(self, project_key, repository_slug, commit_id):
        return self.do_get(self.url_commit_pr, None, (project_key, repository_slug, commit_id))

    