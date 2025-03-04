import logging
from flask import request
from helpers.api_caller_bb import APICallerBB
from helpers.api_caller_jira import APICallerJIRA
import helpers.utils as utils
from models.pullrequest import PullRequest
from server.hmac_resource import HMACResource
import helpers.comment_maker

class DependencyByPR_Comment(HMACResource):
    """ Check and make a comment into the current Pull Request a list of PR Dependencies.
        
        The check is done on all open PRs targeting to the same branch (e.g. master) as the current Pull Request.
        
        Supported events: All Pull Request events

        Method: POST
        Payload: https://confluence.atlassian.com/bitbucketserver062/event-payload-969536923.html

        Note: Maybe able to support newer events from newer Bitbucket versions. Testing is required.

        Request Parameters:
            target: Target branch. Only process the request if the current PR is targetting to this branch. Available value:

                    - master: Restrict to PRs targeting master branch only
                    - any: (Default) No restriction
    """

    CONFIG_SECTION = "BB-WEBHOOK"

    allowed_target = ['any', 'master']
    _logger = logging.getLogger(__name__)

    api_caller_jira: APICallerJIRA
    api_caller:      APICallerBB


    def __init__(self, *args) -> None:
        super().__init__(args)
        self.request_parser.add_argument('target', default='any')
        self.api_caller = APICallerBB(self._config.bitbucket.config)
        if self._config.jira.allow_comment:
            self.api_caller_jira = APICallerJIRA(self._config.jira.config)


    def process_post(self):
        #Get request parameter
        args = self.request_parser.parse_args()
        target = args['target'].lower()

        if target not in self.allowed_target:
            return {'status': 403, 'message': 'target is not allowed'}, 403

        #Only process if JSON payload is found
        if request.is_json:
            payload = self.process_payload()
            #print (payload)

            pr_target = payload.pullRequest.toRef.displayId
            pr_id     = payload.pullRequest.id

            self._logger.info ('Receiving PR event with PR ID: {}, Event: {}, Target: {}'.format(pr_id, payload.eventKey, pr_target))

            if target == 'any' or target == pr_target:
                change_list = self.check_pr_conflicts(payload.pullRequest, target)
                comment = helpers.comment_maker.comment_pr_dependency(change_list, payload.eventKey, payload.date)
                self._logger.debug(f'Comment: {comment}')
                self.api_caller.post_pr_comment(payload.pullRequest.toRef.repository.project.key, payload.pullRequest.toRef.repository.slug, payload.pullRequest.id, comment)
                #Unwatch PR
                self.api_caller.unwatch_pr(payload.pullRequest.toRef.repository.project.key, payload.pullRequest.toRef.repository.slug, payload.pullRequest.id)

                if self._config.jira.allow_comment:
                    jira_key = utils.get_jira_key(payload.pullRequest.fromRef.displayId)
                    if jira_key is not None:
                        self.api_caller_jira.do_jira_comment(jira_key, comment)
                    
                return {'status': 200, 'comment': comment}, 200
            else:
                return {'status': 200, 'message': 'Nothing to do here'}, 200
        else:
            return {'status': 415, 'message': 'Come on! Give me JSON payload!'}, 415


    def check_pr_conflicts(self, pull_request, target):
        project_key = pull_request.toRef.repository.project.key
        repo_slug   = pull_request.toRef.repository.slug
        branch_id   = pull_request.toRef.id

        all_prs = self.api_caller.get_pull_requests(project_key, repo_slug, target_branch=branch_id if target != 'any' else 'any').values
        #Case 1 - No other PR
        #Case 2 - No conflict
        #Case 3 - Have conflict
        if len(all_prs) > 1:
            current_pr_id = pull_request.id
            current_pr_changes = self.api_caller.get_pr_change(project_key, repo_slug, current_pr_id).values
            other_prs = [pr for pr in all_prs if pr.id != current_pr_id]
            
            change_list = []
            for pr in other_prs:
                other_pr_changes = self.api_caller.get_pr_change(project_key, repo_slug, pr.id).values
                #Default is Case 2
                conflict_changes = []
                for current_change in current_pr_changes:
                    #Case 3 if possible
                    conflict_changes.extend([change for change in other_pr_changes if change.path.name ==  current_change.path.name])
                
                change_list.append(PullRequest(pr, conflict_changes))

            return change_list
        else:
            #Case 1
            return []