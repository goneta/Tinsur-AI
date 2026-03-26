
class RequestContext:
    def __init__(self, events=None, metadata=None):
        self.events = events or []
        self.metadata = metadata or {}
