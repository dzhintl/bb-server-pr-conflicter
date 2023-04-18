from datetime import datetime


def comment_pr_dependency(change_list, event_key, event_date):
    comment = '_This is an auto generated message_ \n' \
                f'> * **Event Type:** {event_key}  \n' \
                f'> * **Event Date:** {event_date}  \n\n' \
                f'Excluding the current pull request, there are in total `{len(change_list)}` other active pull requests. '
    
    if len(change_list) > 0:
        comment_pr = ""
        total_confict = 0
        for pull_request in change_list:
            if len(pull_request.file_list) == 0:
                continue
            
            total_confict += 1
            comment_pr += f'## [{pull_request.data.title}]({pull_request.data.links.self[0].href}) \n' \
                        f'* **ID:** {pull_request.data.id} \n' \
                        f'* **From:** `{pull_request.data.fromRef.displayId}` ' \
                            f'(Repository:[{pull_request.data.fromRef.repository.name}]({pull_request.data.fromRef.repository.links.self[0].href}), '\
                            f'Project:[{pull_request.data.fromRef.repository.project.name}]({pull_request.data.fromRef.repository.project.links.self[0].href})) \n' \
                        f'* **To:** `{pull_request.data.toRef.displayId}` ' \
                            f'(Repository:[{pull_request.data.toRef.repository.name}]({pull_request.data.toRef.repository.links.self[0].href}), '\
                            f'Project:[{pull_request.data.toRef.repository.project.name}]({pull_request.data.toRef.repository.project.links.self[0].href})) \n' \
                        f'* **Created Date:** {datetime.utcfromtimestamp(pull_request.data.createdDate/1000)} \n' \
                        f'* **Last Updated:** {datetime.utcfromtimestamp(pull_request.data.updatedDate/1000)} \n' \
                        f'* **Author:** [{pull_request.data.author.user.displayName}]({pull_request.data.author.user.links.self[0].href}) \n' \
                        f'* **Potential Conflict(s):** `{len(pull_request.file_list)}` file(s) \n'
            for change in pull_request.file_list:
                comment_pr += f'  * File `{change.path.name}`, full path at `/{change.path.toString}`. \n'
        
        if total_confict == 0:
            comment += "There is no potential conflict detected. \n"
        else:
            comment += f'There are potential conflicts spotted in `{total_confict}` pull request(s): \n'
            comment += comment_pr

    return comment

