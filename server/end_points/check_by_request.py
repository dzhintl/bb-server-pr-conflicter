import logging
from helpers.api_caller_bb import APICallerBB
from models.pullrequest import PullRequest
from server.apikey_resource import APIKeyResource
import helpers.utils as utils
from flask import request

class DependencyByRequest(APIKeyResource):
    """ Receive ad-hoc requests and response with list of potential conflicts
    """

    SECTION = "BB-ADHOC-REQUEST"

    _logger = logging.getLogger(__name__)

    api_caller: APICallerBB

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.api_caller = APICallerBB(self._config.bitbucket.config)

    def get_config_apikey(self):
        return self._config.key
    

    def get_request_schema(self):
        return utils.json_namespace_to_dict(self._config.request_schema)
    

    def get_header_apikey(self):
        api_key = None
        if 'DS-API-KEY' in request.headers:
            api_key = request.headers['DS-API-KEY']

        return api_key
    

    def process_post(self):
        pay_load = utils.json_namespace_to_dict(self.process_payload())

        project_key = pay_load.project
        file_name   = pay_load.file
        repo_slug   = pay_load.repo

        all_prs = self.api_caller.get_pull_requests(project_key, repo_slug).values

        change_list = []
        #Case 1 - No other PR
        #Case 2 - No conflict
        #Case 3 - Have conflict
        if len(all_prs) > 1:
            for pr in all_prs:
                pr_changes = self.api_caller.get_pr_change(project_key, repo_slug, pr.id).values
                #Default is Case 2
                conflict_changes = []
                #Case 3 if possible
                conflict_changes.extend([change for change in pr_changes if change.path.name ==  file_name])
                if len(conflict_changes) == 0:
                    change_list.append(pr)

        return {"size": len(change_list), "values": change_list}