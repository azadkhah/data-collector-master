class DomainRaw:
    id = None
    domain = None
    tld = None
    try_count = 0
    errors_text = []

    def __init__(self, domain, try_count, tld, errors_text):
        self.tld = tld
        self.domain = domain
        self.try_count = try_count
        self.errors_text = errors_text

    pass
