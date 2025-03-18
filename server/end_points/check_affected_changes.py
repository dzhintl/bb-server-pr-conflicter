import logging
from helpers.api_caller_bb import APICallerBB
from server.apikey_resource import APIKeyResource
import helpers.utils as utils
import helpers.comment_maker as comment_maker
from flask import request

class AffectedChangesAPI(APIKeyResource):
    ''' Receive ad-hoc requests and response with list of affected changes in a commit or PR
    '''

    CONFIG_SECTION = "BB-API-AFFECTED-CHANGES"

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
            
            result = {}

            if hasattr(pay_load, "commit"):
                commit_id = pay_load.commit
                commit_changes = self.api_caller.get_commit_change(project_key, repo_slug, commit_id).values
                # Check error
                if hasattr(commit_changes, "errors"):
                    return {"status": 500, "message": commit_changes.errors[0].message}, 500
                # Add commit changes to result dict
                result["commit"] = {"id": commit_id, "total": len(commit_changes) ,"changes": utils.json_namespace_to_dict(commit_changes)}
            
            if hasattr(pay_load, "pr"):
                pr_id = pay_load.pr
                pr_changes = self.api_caller.get_pr_change(project_key, repo_slug, pr_id).values
                # Check error
                if hasattr(pr_changes, "errors"):
                    return {"status": 500, "message": pr_changes.errors[0].message}, 500
                # Add pr changes to result dict
                result["pr"] = {"id": pr_id, "total": len(pr_changes) ,"changes": utils.json_namespace_to_dict(pr_changes)}

            return {"status":200, "data": result}, 200
        else:
            return {'status': 415, 'message': 'Come on! Give me JSON payload!'}, 415