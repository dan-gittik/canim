from manim import Text
from matplotlib import font_manager
from PIL import ImageFont

from .utils import log


class FontAlignment:
    
    def __init__(self, font: str, font_size: int):
        self.font = font
        self.font_size = font_size
        self.space_width = Text('_' * 100, font=self.font, font_size=self.font_size).width / 100
        self._font = ImageFont.truetype(font_manager.findfont(self.font), self.font_size)
        self._top_margins: dict[str, float] = {}
        self._left_margins: dict[str, float] = {}
        x = Text('x', font=self.font, font_size=self.font_size)
        _, top, _, bottom = self._font.getbbox('x')
        self._ratio = x.height / (bottom - top)
        self.height = x.height + self._ratio * top
        
    def top_margin(self, string: str) -> float:
        string = string.replace(' ', '')
        for char in string:
            if char not in self._top_margins:
                _, top, _, _ = self._font.getbbox(char)
                self._top_margins[char] = self._ratio * top
        margin = min(self._top_margins[char] for char in string)
        return margin

    def left_margin(self, string: str) -> float:
        return self._horizontal_margin(string.strip()[0])

    def right_margin(self, string: str) -> float:
        return self._horizontal_margin(string.strip()[-1])
    
    def _horizontal_margin(self, char: str) -> float:
        if char not in self._left_margins:
            text = Text(char, font=self.font, font_size=self.font_size)
            self._left_margins[char] = self.space_width - text.width
        return self._left_margins[char] / 2