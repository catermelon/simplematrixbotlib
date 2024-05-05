from nio import RoomMessageText


class Message:
    def __init__(self, event: RoomMessageText):
        """@private"""
        self.body = event.body
        self.formatted_body = event.formatted_body
        self.event_id = event.event_id
        self.sender_id = event.sender
        self.args: list[str] = event.body.split()
        self.nio_event = event

    def __repr__(self):
        return self.body
