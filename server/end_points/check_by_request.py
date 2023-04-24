import logging
from helpers.api_caller_bb import APICallerBB
from server.apikey_resource import APIKeyResource
import helpers.utils as utils
import helpers.comment_maker as comment_maker
from flask import request

class DependencyByRequest(APIKeyResource):
    """ Receive ad-hoc requests and response with list of potential conflicts
    """

    CONFIG_SECTION = "BB-ADHOC-REQUEST"

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
    

    def process_post(self):

        if request.is_json:
            pay_load = self.process_payload()

            project_key = pay_load.project
            file_name   = pay_load.file
            repo_slug   = pay_load.repo

            self._logger.info(f'Receiving request to check file: {file_name}, project: {project_key}, repo: {repo_slug}')

            result = self.api_caller.get_pull_requests(project_key, repo_slug)
            if hasattr(result, "errors"):
                return {"status": 200, "comment": result.errors[0].message}, 200

            all_prs = result.values
            #Case 1 - No other PR
            change_list = []
            
            #Case 2 - No conflict
            #Case 3 - Have conflict
            if len(all_prs) > 0:
                for pr in all_prs:
                    pr_changes = self.api_caller.get_pr_change(project_key, repo_slug, pr.id).values
                    #Default is Case 2
                    conflict_changes = []
                    #Case 3 if possible
                    conflict_changes.extend([change for change in pr_changes if change.path.name ==  file_name])
                    if len(conflict_changes) > 0:
                        change_list.append(pr)

            return {"status":200, "comment": comment_maker.comment_dependency(change_list, file_name)}, 200
        else:
            return {'status': 415, 'message': 'Come on! Give me JSON payload!'}, 415