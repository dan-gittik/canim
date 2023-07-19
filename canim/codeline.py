from __future__ import annotations

from manim import Mobject


class CodeLine:

    def __init__(self, block: CodeBlock, text: str):
        self.text = text
        self._block = block
        self._mobject: Mobject = None
    
    def __repr__(self):
        return f'<line {self.number}: {self.text}>'
    
    def __neg__(self) -> CodeBlock:
        self.remove()
    
    def __rshift__(self, *strings: str) -> list[CodeLine]:
        return self.append_lines(*strings)

    def __lshift__(self, *strings: str) -> list[CodeLine]:
        return self.prepend_lines(*strings)

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


class CodeLineGroup:

    def __init__(self, block: CodeBlock, lines: list[CodeLine]):
        self._block = block
        self._lines = lines
    
    def __repr__(self):
        return f'<line group: {", ".join(str(line.number) for line in self._lines)}>'
    
    def __neg__(self) -> CodeLineGroup:
        self.remove()
    
    def __rshift__(self, *strings: str) -> list[CodeLine]:
        return self.last_line.append_lines(*strings)
    
    def __lshift__(self, *strings: str) -> list[CodeLine]:
        return self.first_line.prepend_lines(*strings)
    
    @property
    def first_line(self) -> CodeLine:
        return min(self._lines, key=lambda line: line.index)
    
    @property
    def last_line(self) -> CodeLine:
        return max(self._lines, key=lambda line: line.index)
    
    def remove(self) -> None:
        self._block.remove_lines(*self._lines)
    

from .codeblock import CodeBlock