import logging
import time
from flask import request
from server.end_points.check_by_pr import DependencyByPR
import helpers.comment_maker
import helpers.utils as utils


class DependencyByCommit(DependencyByPR):
    """ Check and make a comment into Pull Request of the current commit a list of PR Dependencies.
        
        The check is done on all open PRs targeting to the same branch (e.g. master) as the Pull Request of the current commit.
        
        Supported events: Repository Events -> Push (repo:refs_changed)

        Method: POST
        Payload: https://confluence.atlassian.com/bitbucketserver062/event-payload-969536923.html

        Request Parameters:
            target: Target branch. Only process the request if PR of the current commit is targetting to this branch. Available value:

                    - master: Restrict to PRs targeting master branch only
                    - any: (Default) No restriction
    """

    _logger = logging.getLogger(__name__)

    def process_post(self):
        #Get request parameter
        args = self.request_parser.parse_args()
        target = args['target'].lower()

        if target not in self.allowed_target:
            return {'status': 403, 'message': 'target is not allowed'}, 403

        #Only process if JSON payload is found
        if request.is_json:
            payload = self.process_payload()

            commit_id    = payload.changes[0].toHash
            project_key  = payload.repository.project.key
            repo_slug    = payload.repository.slug

            self._logger.info ('Receiving event {} with commit ID: {}'.format(payload.eventKey, commit_id))
            time.sleep(1)
            pr_list = self.api_caller.get_commit_pr(project_key, repo_slug, commit_id).values

            open_prs = []
            open_prs.extend([pr for pr in pr_list if pr.state=='OPEN'])
            prs = []
            if target == 'master':
                prs.extend([pr for pr in open_prs if pr.toRef.displayId == target])
            elif target == 'any':
                prs.extend(open_prs)

            if len(prs) > 0:
                comments = []
                for pr in prs:
                    comment = helpers.comment_maker.comment_pr_dependency(self.check_pr_conflicts(pr, target), payload.eventKey, payload.date)
                    comments.append(comment)
                    self._logger.debug(f'PR ID: {pr.id}, Comment: {comment}')
                    self.api_caller.post_pr_comment(project_key, repo_slug, pr.id, comment)
                    #Unwatch PR
                    self.api_caller.unwatch_pr(project_key, repo_slug, pr.id)
                    
                    if self._config.jira.allow_comment:
                        jira_key = utils.get_jira_key(payload.changes[0].ref.displayId)
                        if jira_key is not None:
                            self.api_caller_jira.do_jira_comment(jira_key, comment)
                
                return {'status': 200, 'comment': comments}, 200
            else:
                return {'status': 200, 'message': 'Nothing to do here'}, 200
        else:
            return {'status': 415, 'message': 'Come on! Give me JSON payload!'}, 415