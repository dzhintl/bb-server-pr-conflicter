import logging
from helpers.api_caller_bb import APICallerBB
from server.apikey_resource import APIKeyResource
import helpers.utils as utils
import helpers.comment_maker as comment_maker
from flask import request

class DependencyByRequest(APIKeyResource):
    """ Receive ad-hoc requests to check if a file is in conflict with other PRs and return the result as JSON
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
    

    def process_get(self):

        if request.is_json:
            pay_load = self.process_payload()

            project_key = pay_load.project
            # if pay_load.files is found, use it, otherwise use pay_load.file
            if hasattr(pay_load, "files"):
                file_list = pay_load.files
            else:
                file_list = [pay_load.file]
            repo_slug   = pay_load.repo

            self._logger.info(f'Receiving request to check list of files: {file_list}, project: {project_key}, repo: {repo_slug}')

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
                    conflict_changes_list = []
                    #Case 3 if possible
                    # Go through all files in the PR
                    for file_name in file_list:
                        conflict_changes = []
                        conflict_changes.extend([change for change in pr_changes if change.path.name ==  file_name])
                        
                        if len(conflict_changes) > 0:
                            conflict_changes_list.append({"file": file_name, "changes": conflict_changes})
                    
                    if len(conflict_changes_list) > 0:
                        #reduce pr to only id, title, author, and link
                        change_list.append({"pr": pr, "conflicts": conflict_changes_list})

            return {"status":200, "total": len(change_list) , "data": utils.json_namespace_to_dict(change_list)}, 200
        else:
            return {'status': 415, 'message': 'Come on! Give me JSON payload!'}, 415