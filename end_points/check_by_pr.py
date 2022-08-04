from flask import request
from helpers.bb_api_caller import BBAPICaller
from models.pullrequest import PullRequest
from server.api_server import HMACResource, Credential
import helpers.bb_comment_maker

class DependencyByPR(HMACResource):
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

    allowed_target = ['any', 'master']

    def __init__(self, cred: Credential, api_caller: BBAPICaller) -> None:
        super().__init__(cred, api_caller)
        self.request_parser.add_argument('target', default='any')

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

            #TODO: Change to logger
            print ('ID: {}, Event: {}, Target: {}'.format(pr_id, payload.eventKey, pr_target))

            if target == 'any' or target == pr_target:
                change_list = self.check_pr_conflicts(payload.pullRequest)
                comment = helpers.bb_comment_maker.comment_pr_dependency(change_list, payload.eventKey, payload.date)
                self.api_caller.post_pr_comment(payload.pullRequest.toRef.repository.project.key, payload.pullRequest.toRef.repository.slug, payload.pullRequest.id, comment)
                return {'status': 200, 'comment': comment}, 200
            else:
                return {'status': 200, 'message': 'Nothing to do here'}, 200
        else:
            return {'status': 415, 'message': 'Come on! Give me JSON payload!'}, 415


    def check_pr_conflicts(self, pull_request):
        project_key = pull_request.toRef.repository.project.key
        repo_slug   = pull_request.toRef.repository.slug
        branch_id   = pull_request.toRef.id

        all_prs = self.api_caller.get_pull_requests(project_key, repo_slug, branch_id).values
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