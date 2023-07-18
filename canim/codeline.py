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

    def prepend_lines(self, *strings: str) -> CodeLine:
        if self.index == 0:
            self._block.prepend_lines(*strings)
        else:
            return self._block.insert_lines(self.index, *strings)
   
    def append_lines(self, *strings: str) -> CodeLine:
        return self._block.insert_lines(self.index + 1, *strings)
        
    def remove(self) -> None:
        self._block.remove_lines(self)
    

from .codeblock import CodeBlock