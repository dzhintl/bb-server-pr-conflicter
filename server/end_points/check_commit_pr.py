import logging
from helpers.api_caller_bb import APICallerBB
from server.apikey_resource import APIKeyResource
import helpers.utils as utils
import helpers.comment_maker as comment_maker
from flask import request

class CommitPR(APIKeyResource):
    ''' Receive ad-hoc requests and response with list of PRs for a commit
    '''

    CONFIG_SECTION = "BB-API-COMMIT-PR"

    _logger = logging.getLogger(__name__)

    api_caller: APICallerBB

    def __init__(self, *args) -> None:
        super().__init__(*args)
        self.api_caller = APICallerBB(self._config.bitbucket.config)

    def get_config_apikey(self):
        if self._config.api_key.key:
            return utils.base64_decode(self._config.api_key.key)
        else:
            return ""
    

    def get_request_schema(self):
        return utils.json_namespace_to_dict(self._config.request_schema)
    

    def get_header_apikey(self):
        api_key = ""
        if self._config.api_key.header and self._config.api_key.header in request.headers:
                api_key = request.headers[self._config.api_key.header]

        return api_key
    

    def process_get(self):

        if request.is_json:
            pay_load = self.process_payload()

            project_key = pay_load.project
            repo_slug   = pay_load.repo      

            commit_id = pay_load.commit
            pr_list = self.api_caller.get_commit_pr(project_key, repo_slug, commit_id).values
            # Check error
            if hasattr(pr_list, "errors"):
                return {"status": 500, "message": pr_list.errors[0].message}, 500
            
             # If payload does not have status, default to return all PRs
            if hasattr(pay_load, "status"):
                pr_list = [pr for pr in pr_list if pr.state==pay_load.status]

            # If payload does not have target, default to return all PRs
            if hasattr(pay_load, "target"):
                pr_list = [pr for pr in pr_list if pr.toRef.displayId == pay_load.target]

            return {"status":200, "total": len(pr_list) ,"data": utils.json_namespace_to_dict(pr_list)}, 200
        else:
            return {'status': 415, 'message': 'Come on! Give me JSON payload!'}, 415