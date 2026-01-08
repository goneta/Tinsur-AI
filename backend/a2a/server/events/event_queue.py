class EventQueue:
    def __init__(self):
        self.events = []

    def enqueue_event(self, event):
        # print(f"Event Enqueued: {event}")
        self.events.append(event)
