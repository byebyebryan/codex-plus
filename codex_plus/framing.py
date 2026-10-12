"""Bounded UTF-8 occurrence framing across native output chunks."""

class Lines:
    def __init__(self, limit: int = 4096):
        self.limit = limit
        self.buffer = b''

    def feed(self, data: bytes, *, eof: bool = False) -> list[str]:
        self.buffer += data
        parts = self.buffer.split(b'\n')
        self.buffer = b'' if eof else parts.pop()
        if len(self.buffer) > self.limit or any(len(p) > self.limit for p in parts):
            raise ValueError('event exceeds byte limit')
        return [p.decode('utf-8') for p in parts if p.strip()]

