from nio import RoomMessageText
import re


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

    def get_body(self):
        if self.formatted_body and "<mx-reply>" in self.formatted_body:
            return re.sub(r'<mx-reply>.*?</mx-reply>', '', self.formatted_body)
        return self.body

    def contains(self, string, regex: bool = False, case_sensitive: bool = True):
        body = self.get_body() if case_sensitive else self.get_body().lower()

        if regex:
            return bool(re.search(string, body, 0 if case_sensitive else re.IGNORECASE))

        if not isinstance(string, str):
            return any(body in (a if case_sensitive else a.lower()) for a in string)

        return (string if case_sensitive else string.lower()) in body
