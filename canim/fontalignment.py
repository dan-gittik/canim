import textwrap

from manim import Text
from matplotlib import font_manager
from PIL import ImageFont


class FontAlignment:
    
    def __init__(
            self,
            font: str,
            font_size: int,
            paragraph_font: str = None,
            paragraph_size: int = None,
    ):
        self.font = font
        self.font_size = font_size
        self.paragraph_font = paragraph_font or font
        self.paragraph_size = paragraph_size or font_size
        self.space_width = Text('_' * 100, font=self.font, font_size=self.font_size).width / 100
        self._font = self._load_font(self.font, self.font_size)
        self._paragraph_font = self._load_font(self.paragraph_font, self.paragraph_size)
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
    
    def wrap_paragraph(self, width: float, text: str) -> str:
        output: list[str] = []
        for line in text.splitlines():
            average = Text(line, font=self.paragraph_font, font_size=self.paragraph_size).width / len(line)
            output.append(textwrap.fill(line, int(width / average)))
        return '\n'.join(output)
    
    def _load_font(self, font: str, font_size: int) -> ImageFont.FreeTypeFont:
        return ImageFont.truetype(font_manager.findfont(font), font_size)

    def _horizontal_margin(self, char: str) -> float:
        if char not in self._left_margins:
            text = Text(char, font=self.font, font_size=self.font_size)
            self._left_margins[char] = self.space_width - text.width
        return self._left_margins[char] / 2