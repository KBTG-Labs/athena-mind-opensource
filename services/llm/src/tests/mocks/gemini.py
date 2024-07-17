from dataclasses import dataclass


@dataclass
class MockGeminiResponse:
    text: str

    def __str__(self):
        return self.text
    
    __repr__ = __str__