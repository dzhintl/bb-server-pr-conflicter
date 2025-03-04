from datetime import datetime
import markdown_strings


def comment_pr_dependency(change_list, event_key, event_date):
    comment = f'{markdown_strings.italics("This is an auto generated message")} \n' \
                f'{markdown_strings.blockquote(markdown_strings.unordered_list(["Event Type: " + event_key, "Event Date: " + event_date]))}\n\n' \
                f'Excluding the current pull request, there are in total {markdown_strings.inline_code(len(change_list))} other active pull requests. '
    
    if len(change_list) > 0:
        comment_pr = ""
        total_confict = 0
        for pull_request in change_list:
            if len(pull_request.file_list) == 0:
                continue
            
            total_confict += 1
            comment_pr += f'## {markdown_strings.link(pull_request.data.title, pull_request.data.links.self[0].href)} \n' \
                        f'* {markdown_strings.bold("ID:")} {pull_request.data.id} \n' \
                        f'* {markdown_strings.bold("From:")} {markdown_strings.inline_code(pull_request.data.fromRef.displayId)} ' \
                            f'(Repository: {markdown_strings.link(pull_request.data.fromRef.repository.name, pull_request.data.fromRef.repository.links.self[0].href)}, '\
                            f'Project:{markdown_strings.link(pull_request.data.fromRef.repository.project.name, pull_request.data.fromRef.repository.project.links.self[0].href)}) \n' \
                        f'* {markdown_strings.bold("To:")} {markdown_strings.inline_code(pull_request.data.toRef.displayId)} ' \
                            f'(Repository:{markdown_strings.link(pull_request.data.toRef.repository.name, pull_request.data.toRef.repository.links.self[0].href)}, '\
                            f'Project:{markdown_strings.link(pull_request.data.toRef.repository.project.name, pull_request.data.toRef.repository.project.links.self[0].href)}) \n' \
                        f'* {markdown_strings.bold("Created Date:")} {datetime.utcfromtimestamp(pull_request.data.createdDate/1000)} \n' \
                        f'* {markdown_strings.bold("Last Updated:")} {datetime.utcfromtimestamp(pull_request.data.updatedDate/1000)} \n' \
                        f'* {markdown_strings.bold("Author:")} {markdown_strings.link(pull_request.data.author.user.displayName, pull_request.data.author.user.links.self[0].href)} \n' \
                        f'* {markdown_strings.bold("Potential Conflict(s):")} {markdown_strings.inline_code(len(pull_request.file_list))} file(s) \n'
            for change in pull_request.file_list:
                comment_pr += f'  * File {markdown_strings.inline_code(change.path.name)}, full path at {markdown_strings.inline_code("/" + change.path.toString)}. \n'
        
        if total_confict == 0:
            comment += "There is no potential conflict detected. \n"
        else:
            comment += f'There are potential conflicts spotted in {markdown_strings.inline_code(total_confict)} pull request(s): \n'
            comment += comment_pr

    return comment


def comment_dependency(change_list, file_name):
    comment = f'Conflict checking report for file {markdown_strings.inline_code(file_name)}:\n\n' \
              
    if len(change_list) > 0:
        comment += f'There are in total {len(change_list)} active pull requests that have modified this file:\n'
        for pull_request in change_list:
            comment += f'\n{markdown_strings.link(pull_request.title,pull_request.links.self[0].href)} \n' \
                            f'- ID: {pull_request.id} \n' \
                            f'- From: {markdown_strings.esc_format(pull_request.fromRef.displayId, True)} ' \
                                f'(Repository:{markdown_strings.link(pull_request.fromRef.repository.name, pull_request.fromRef.repository.links.self[0].href)}) \n'\
                            f'- To: {markdown_strings.esc_format(pull_request.toRef.displayId, True)} ' \
                                f'(Repository:{markdown_strings.link(pull_request.toRef.repository.name, pull_request.toRef.repository.links.self[0].href)}) \n'\
                            f'- Created Date: {datetime.utcfromtimestamp(pull_request.createdDate/1000)} \n' \
                            f'- Last Updated: {datetime.utcfromtimestamp(pull_request.updatedDate/1000)} \n' \
                            f'- Author: {markdown_strings.link(pull_request.author.user.displayName, pull_request.author.user.links.self[0].href)} \n'
    else:
        comment += "There is no potential conflict detected."

    return comment