class PullRequest:
    data: None
    file_list: None
    def __init__(self, data, file_list=[]) -> None:
        self.data = data
        self.file_list = file_list
