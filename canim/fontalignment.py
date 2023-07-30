from manim import MarkupText


class FontAlignment:
    
    def __init__(self, font: str, font_size: int):
        self.font = font
        self.font_size = font_size
    
    def top_margin(self, text: MarkupText) -> float:
        pass

    def left_margin(self, text: MarkupText) -> float:
        return self._horizontal_margin(text.text[0])

    def right_margin(self, text: MarkupText) -> float:
        return self._horizontal_margin(text.text[-1])
    
    def _horizontal_margin(self, text: str) -> float:
        pass