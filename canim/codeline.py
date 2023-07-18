from __future__ import annotations

from manim import Mobject


class CodeLine:

    def __init__(self, block: CodeBlock, text: str):
        self.text = text
        self._block = block
        self._mobject: Mobject = None
    
    def __repr__(self):
        return f'<line {self.number}: {self.text}>'
    
    @property
    def index(self):
        return self._block._lines.index(self)
    
    @property
    def number(self) -> int:
        return self.index + 1


from .codeblock import CodeBlock