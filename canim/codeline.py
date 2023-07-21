from __future__ import annotations
from typing import ContextManager, Pattern

from manim import Mobject


class CodeLine:

    def __init__(self, block: CodeBlock, text: str):
        self.text = text
        self._block = block
        self._mobject: Mobject = None
    
    def __repr__(self):
        return f'<line {self.number or "*"}: {self.text}>'

    def __enter__(self):
        self._context = self.highlight()
        self._context.__enter__()
        return self
    
    def __exit__(self, exception, error, traceback):
        return self._context.__exit__(exception, error, traceback)
    
    def __neg__(self) -> CodeBlock:
        self.remove()
        return self
    
    def __invert__(self) -> CodeBlock:
        self.scroll_into_view()
        return self
    
    def __lt__(self, strings: str|tuple[str]) -> CodeBlock:
        if not isinstance(strings, tuple):
            strings = strings,
        self.replace(*strings)
        return self

    def __mul__(self, pattern: str|Pattern) -> ContextManager[None]:
        return self.highlight(pattern=pattern)
 
    def __rshift__(self, *strings: str) -> list[CodeLine]:
        return self.append_lines(*strings)

    def __lshift__(self, *strings: str) -> list[CodeLine]:
        return self.prepend_lines(*strings)

    @property
    def index(self) -> None|int:
        try:
            return self._block._lines.index(self)
        except ValueError:
            return None
    
    @property
    def number(self) -> None|int:
        return self.index + 1 if self.index is not None else None
    
    def prepend_lines(self, *strings: str) -> list[CodeLine]:
        if self.index == 0:
            self._block.prepend_lines(*strings)
        else:
            return self._block.insert_lines(self.index, *strings)
   
    def append_lines(self, *strings: str) -> list[CodeLine]:
        return self._block.insert_lines(self.index + 1, *strings)
        
    def remove(self) -> None:
        self._block.remove_lines([self])
    
    def replace(self, *strings: str) -> list[CodeLine]:
        return self._block.replace_lines([self], *strings)
    
    def scroll_into_view(self) -> None:
        self._block.scroll_into_view(self)
    
    def highlight(self, pattern: str|Pattern = None) -> ContextManager[None]:
        if pattern is not None:
            return self._block.highlight_pattern(pattern, [self])
        else:
            return self._block.highlight_lines([self], pattern=pattern)


class CodeLineGroup:

    def __init__(self, block: CodeBlock, lines: list[CodeLine]):
        self._block = block
        self._lines = lines
        self._lines.sort(key=lambda line: line.index)
        self._context: ContextManager[None] = []
    
    def __repr__(self):
        return f'<line group: {", ".join(str(line.number) for line in self._lines)}>'
    
    def __enter__(self):
        self._context = self.highlight()
        self._context.__enter__()
        return self
    
    def __exit__(self, exception, error, traceback):
        return self._context.__exit__(exception, error, traceback)
    
    def __lt__(self, strings: str|tuple[str]):
        if not isinstance(strings, tuple):
            strings = strings,
        return self.replace(*strings)
    
    def __neg__(self) -> CodeLineGroup:
        self.remove()
        return self
    
    def __invert__(self) -> CodeLineGroup:
        self.scroll_into_view()
        return self
    
    def __mul__(self, pattern: str|Pattern) -> ContextManager[None]:
        return self.highlight(pattern=pattern)
    
    def __rshift__(self, *strings: str) -> list[CodeLine]:
        return self._lines[-1].append_lines(*strings)
    
    def __lshift__(self, *strings: str) -> list[CodeLine]:
        return self._lines[0].prepend_lines(*strings)
    
    def remove(self) -> None:
        self._block.remove_lines(self._lines)
    
    def replace(self, *strings: str) -> None:
        self._block.replace_lines(self._lines, *strings)
    
    def scroll_into_view(self) -> None:
        self._block.scroll_into_view(self._lines[0], self._lines[-1])
    
    def highlight(self, pattern: str|Pattern = None) -> ContextManager[None]:
        if pattern is not None:
            return self._block.highlight_pattern(pattern, self._lines)
        else:
            return self._block.highlight_lines(self._lines)
    

from .codeblock import CodeBlock