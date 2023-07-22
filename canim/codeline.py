from __future__ import annotations
from typing import Any, ContextManager, Pattern

import re

from manim import Mobject

from .utils import split_lines


class CodeLine:

    _enclosed_pattern = re.compile(r'^(\s*)\{\.\.\.\}$')

    def __init__(self, block: CodeBlock, text: str):
        self.text = text
        self._block = block
        self._mobject: Mobject = None
        self._stash: dict[str, Any] = {}
    
    def __repr__(self):
        return f'<line {self.number or "*"}: {self.text}>'

    def __enter__(self):
        self._context = self.highlight()
        self._context.__enter__()
        return self
    
    def __exit__(self, exception, error, traceback):
        return self._context.__exit__(exception, error, traceback)
    
    def __lt__(self, strings: str|tuple[str]) -> CodeBlock:
        if not isinstance(strings, tuple):
            strings = strings,
        self.replace(*strings)
        return self
    
    def __call__(self, **stash: Any) -> CodeLine:
        self._stash = stash
        return self

    def __neg__(self) -> CodeBlock:
        self.remove()
        return self
    
    def __invert__(self) -> CodeBlock:
        self.scroll_into_view()
        return self
    
    def __mul__(self, pattern: str|Pattern) -> ContextManager[None]:
        return self.highlight(pattern)
 
    def __floordiv__(self, enclosing_lines: tuple[str, str]) -> list[CodeLine]:
        before, after, indent = self._split_enclosing(enclosing_lines)
        lines = self.enclose([self], before, after, indent=indent, **self._stash)
        self._stash.clear()
        return lines

    def __rshift__(self, *strings: str) -> list[CodeLine]:
        lines = self.append_lines(*strings, **self._stash)
        self._stash.clear()
        return lines

    def __lshift__(self, *strings: str) -> list[CodeLine]:
        lines = self.prepend_lines(*strings, **self._stash)
        self._stash.clear()
        return lines
    
    @property
    def index(self) -> None|int:
        try:
            return self._block._lines.index(self)
        except ValueError:
            return None
    
    @property
    def number(self) -> None|int:
        return self.index + 1 if self.index is not None else None
    
    def prepend_lines(
            self,
            *strings: str,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        if self.index == 0:
            self._block.prepend_lines(*strings,
                raw = raw,
                at_once = at_once,
            )
        else:
            return self._block.insert_lines(self.index, *strings,
                raw = raw,
                at_once = at_once,
            )
   
    def append_lines(
            self,
            *strings: str,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        return self._block.insert_lines(self.index + 1, *strings,
            raw = raw,
            at_once = at_once,
        )
        
    def remove(self) -> None:
        self._block.remove_lines([self])
    
    def replace(
            self,
            *strings: str,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        return self._block.replace_lines([self], *strings,
            raw = raw,
            at_once = at_once,
        )
    
    def enclose(
            self,
            before: str,
            after: str,
            *,
            indent: int = None,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        return self._block.enclose_lines([self], before, after,
            indent = indent,
            raw = raw,
            at_once = at_once,
        )
    
    def scroll_into_view(self) -> None:
        self._block.scroll_into_view(self)
    
    def highlight(self, pattern: str|Pattern = None) -> ContextManager[None]:
        if pattern is not None:
            return self._block.highlight_pattern(pattern, [self])
        else:
            return self._block.highlight_lines([self], pattern=pattern)
    
    @classmethod
    def _split_enclosing(cls, string: str) -> tuple[list[str], list[str], int]:
        before: list[CodeLine] = []
        after: list[CodeLine] = []
        indent: int = None
        lines = before
        for text in split_lines(string):
            match = cls._enclosed_pattern.match(text)
            if match:
                whitespace, = match.groups()
                indent = len(whitespace)
                lines = after
                continue
            lines.append(text)
        return before, after, indent


class CodeLineGroup:

    def __init__(self, block: CodeBlock, lines: list[CodeLine]):
        self._block = block
        self._lines = lines
        self._lines.sort(key=lambda line: line.index)
        self._context: ContextManager[None] = []
        self._stash: dict[str, Any] = {}
    
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
    
    def __call__(self, **stash: Any) -> CodeLineGroup:
        self._stash = stash
        return self
    
    def __neg__(self) -> CodeLineGroup:
        self.remove()
        return self
    
    def __invert__(self) -> CodeLineGroup:
        self.scroll_into_view()
        return self
    
    def __mul__(self, pattern: str|Pattern) -> ContextManager[None]:
        return self.highlight(pattern=pattern)
    
    def __floordiv__(self, enclosing_lines: tuple[str, str]) -> list[CodeLine]:
        before, after, indent = CodeLine._split_enclosing(enclosing_lines)
        lines = self.enclose(before, after, indent=indent, **self._stash)
        self._stash.clear()
        return lines
    
    def __rshift__(self, *strings: str) -> list[CodeLine]:
        return self._lines[-1].append_lines(*strings)
    
    def __lshift__(self, *strings: str) -> list[CodeLine]:
        return self._lines[0].prepend_lines(*strings)
    
    @property
    def is_consecutive(self) -> bool:
        index = self._lines[0].index
        for line in self._lines:
            if line.index != index:
                return False
            index += 1
        return True

    def remove(self) -> None:
        self._block.remove_lines(self._lines)
    
    def replace(
            self,
            *strings: str,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        return self._block.replace_lines(self._lines, *strings,
            raw = raw,
            at_once = at_once,
        )
    
    def enclose(
            self,
            before: str,
            after: str,
            *,
            indent: int = None,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        if not self.is_consecutive:
            raise ValueError('can only enclose consecutive lines')
        return self._block.enclose_lines(self._lines, before, after,
            indent = indent,
            raw = raw,
            at_once = at_once,
        )
    
    def scroll_into_view(self) -> None:
        self._block.scroll_into_view(self._lines[0], self._lines[-1])
    
    def highlight(self, pattern: str|Pattern = None) -> ContextManager[None]:
        if pattern is not None:
            return self._block.highlight_pattern(pattern, self._lines)
        else:
            return self._block.highlight_lines(self._lines)
    

from .codeblock import CodeBlock