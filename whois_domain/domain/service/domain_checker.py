class DomainChecker:
    success_list = {}
    error_list = {}
    queued_list = {}

    def __init__(self, *, success_list=None, error_list=None, queued_list=None):
        if success_list:
            self.success_list = success_list

        if error_list:
            self.error_list = error_list

        if (queued_list):
            self.queued_list = queued_list

    def exist(self, domain):
        if domain in self.success_list or domain in self.error_list or domain in self.queued_list:
            return True
        else:
            return False


