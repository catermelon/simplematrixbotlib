"""@private"""

class EvalMe:
    def __init__(self, to_eval: str):
        self.to_eval = to_eval

    def __repr__(self):
        return f'<EvalMe: {self.to_eval}>'
