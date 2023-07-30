from __future__ import annotations
from typing import Any, ContextManager, Pattern

import re

from manim import (
    UL,
    DOWN,
    RIGHT,
    Mobject,
    Group,
    MarkupText,
    FadeIn,
    FadeOut,
    AddTextLetterByLetter,
)
from manim.mobject.text.text_mobject import remove_invisible_chars

from .utils import split_lines


class CodeLine:

    def __init__(
            self,
            block: CodeBlock,
            text: MarkupText,
            indent: int = None,
            prompt: MarkupText = None,
    ):
        if indent is None:
            indent = 0
        self.block = block
        self.text = text
        self.indent = indent
        self.prompt = prompt
        self._stash: dict[str, Any] = {}
    
    def __repr__(self):
        return f'<line {self.index or "*"}: {self.string}>'

    def __enter__(self):
        self._context = self.highlight(**self._stash)
        self._stash.clear()
        return self._context.__enter__()
    
    def __exit__(self, exception, error, traceback):
        return self._context.__exit__(exception, error, traceback)

    def __call__(self, **stash: Any) -> CodeLine:
        self._stash = stash
        return self
    
    def __lt__(self, string: str) -> list[CodeLine]:
        lines = self.replace(string, **self._stash)
        self._stash.clear()
        return lines

    def __neg__(self) -> CodeBlock:
        self.remove(**self._stash)
        self._stash.clear()
        return self
    
    def __invert__(self) -> CodeBlock:
        self.scroll_into_view(**self._stash)
        self._stash.clear()
        return self
    
    def __mul__(self, pattern: str|Pattern) -> ContextManager[None]:
        context = self.highlight(pattern, **self._stash)
        self._stash.clear()
        return context
 
    def __floordiv__(self, enclosure: str) -> list[CodeLine]:
        before, after, prompt, indent = split_enclosure(self.block.config.prompt_pattern, enclosure)
        lines = self.enclose(
            before = before,
            after = after,
            prompt = prompt,
            indent = indent,
            **self._stash,
        )
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
    
    @classmethod
    def parse(cls, block: CodeBlock, line: str, plain: bool = None) -> CodeLine:
        if plain is None:
            plain = block.config.syntax_highlighting
        prompt = None
        prefix, whitespace, content = re.match(f'^({block.config.prompt_pattern})?(\s*)(.*)$', line).groups()
        if not plain:
            if block._syntax_highlighter:
                content = block._syntax_highlighter.highlight(content)
            if prefix:
                prompt = block._create_text(prefix)
        text = block._create_text(content)
        # text.z_index = self.z_index + 2
        return cls(
            block = block,
            text = text,
            prompt = prompt,
            indent = len(whitespace),
        )

    @property
    def string(self) -> str:
        output: list[str] = []
        if self.prompt:
            output.append(self.prompt.text)
        if self.indent:
            output.append(' ' * self.indent)
        output.append(self.text.text)
        return ''.join(output)
    
    @property
    def index(self) -> None|int:
        try:
            return self.block.lines.index(self)
        except ValueError:
            return None
        
    @property
    def top(self) -> float:
        return self.text.get_top()[1] # + font_offset
    
    @property
    def left(self) -> float:
        if self.prompt:
            mobject = self.prompt
        else:
            mobject = self.text
        return mobject.get_left()[0] # + font_offset
    
    @property
    def bottom(self) -> float:
        return self.text.get_bottom()[1] + self.block.theme.line_gap
    
    @property
    def right(self) -> float:
        return self.text.get_right()[0] # + font_offset

    @property
    def height(self) -> float:
        return self.top - self.bottom
    
    @property
    def width(self) -> float:
        return self.right - self.left
    
    @property
    def typing_duration(self) -> float:
        printable = remove_invisible_chars(self.text.text).replace(' ', '')
        return len(printable) * self.block.config.typing_speed

    def scroll_into_view(self) -> None:
        self.block.scroll_into_view(self)
    
    def prepend_lines(
            self,
            *strings: str,
            indent_lines: int|CodeLineGroup|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        if self.index == 0:
            return self.block.prepend_lines(
                *strings,
                indent_lines = indent_lines,
                indent_level = indent_level,
                indent_prompt = indent_prompt,
                plain = plain,
            )
        return self.block.insert_lines(
            self.index,
            *strings,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
   
    def append_lines(
            self,
            *strings: str,
            indent_lines: int|CodeLineGroup|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.block.insert_lines(
            self.index + 1,
            *strings,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
        
    def remove(self) -> None:
        self.block.remove_lines([self])
    
    def replace(
            self,
            *strings: str,
            indent_lines: int|CodeLineGroup|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.block.replace_lines(
            [self],
            *strings,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
    
    def enclose(
            self,
            before: str,
            after: str,
            *,
            indent: int = None,
            prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.block.enclose_lines(
            lines = [self],
            before = before,
            after = after,
            indent = indent,
            prompt = prompt,
            plain = plain,
        )
    
    def highlight(self, pattern: str|Pattern = None) -> ContextManager[None]:
        if pattern is not None:
            return self.block.highlight_pattern(pattern, [self])
        else:
            return self.block.highlight_lines([self])
    
    @property
    def _mobject(self) -> Mobject:
        if self.prompt is None:
            return self.text
        return Group(self.prompt, self.text)
    
    def _position(self, top: float, left: float) -> None:
        fa = self.block._font_alignment
        top_margin = fa.top_margin(self.string)
        if self.prompt:
            self.prompt.move_to([
                top + top_margin,
                left + fa.left_margin(self.prompt),
                0,
            ], UL)
            self.text.move_to([
                top + top_margin,
                self.prompt.get_right()[0] + fa.right_margin(self.prompt) + fa.left_margin(self.text),
                0,
            ], UL)
        else:
            self.text.move_to([
                top + top_margin,
                left + fa.left_margin(self.text),
                0,
            ], UL)
        self.text.shift(fa.space_width * self.indent * RIGHT)

    def _slide(self, offset: float):
        self._mobject.shift(offset * DOWN)
    
    def _animate_insert(self, plain: bool = None) -> None:
        if plain:
            self.block._add_transition(FadeIn(self._mobject))
        else:
            if self.prompt:
                self.block.scene.add(self.prompt)
            self.block.scene.play(AddTextLetterByLetter(self.text), run_time=self.typing_duration)

    def _animate_remove(self, replace_with: CodeLine=None) -> None:
        if self.prompt and replace_with.prompt and self.prompt.text == replace_with.prompt.text:
            replace_with.prompt = self.prompt
            mobject = self.text
        else:
            mobject = self._mobject
        self.block._add_transition(FadeOut(mobject))
    
    def _animate_slide(
            self,
            offset: float,
            indent: int = None,
            prompt: str = None,
    ) -> None:
        pass

    def _animate_opacity(self, opacity: float) -> None:
        self.block._add_transition(self._mobject.animate.set_opacity(opacity))


class CodeLineGroup:

    def __init__(self, block: CodeBlock, lines: list[CodeLine]):
        self.block = block
        self.lines = lines
        self.lines.sort(key=lambda line: line.index)
        self._stash: dict[str, Any] = {}
    
    def __repr__(self):
        return f'<line group: {", ".join(str(line.index) for line in self.lines)}>'
    
    def __enter__(self):
        self._context = self.highlight(**self._stash)
        self._stash.clear()
        return self._context.__enter__()
    
    def __exit__(self, exception, error, traceback):
        return self._context.__exit__(exception, error, traceback)
    
    def __call__(self, **stash: Any) -> CodeLineGroup:
        self._stash = stash
        return self
    
    def __lt__(self, string: str) -> list[CodeLine]:
        lines = self.replace(string, **self._stash)
        self._stash.clear()
        return lines
    
    def __neg__(self) -> CodeLineGroup:
        self.remove(**self._stash)
        self._stash.clear()
        return self
    
    def __invert__(self) -> CodeLineGroup:
        self.scroll_into_view(**self._stash)
        self._stash.clear()
        return self
    
    def __mul__(self, pattern: str|Pattern) -> ContextManager[None]:
        context = self.highlight(pattern=pattern, **self._stash)
        self._stash.clear()
        return context
    
    def __floordiv__(self, enclosure: str) -> list[CodeLine]:
        before, after, prompt, indent = split_enclosure(self.block.config.prompt_pattern, enclosure)
        lines = self.enclose(
            before = before,
            after = after,
            indent = indent,
            prompt = prompt,
            **self._stash,
        )
        self._stash.clear()
        return lines
    
    def __rshift__(self, string: str) -> list[CodeLine]:
        lines = self.lines[-1].append_lines(string, **self._stash)
        self._stash.clear()
        return lines
    
    def __lshift__(self, string: str) -> list[CodeLine]:
        lines = self.lines[0].prepend_lines(string, **self._stash)
        self._stash.clear()
        return lines
    
    def scroll_into_view(self) -> None:
        self.block.scroll_into_view(self.lines[0], self.lines[-1])
    
    def remove(self) -> None:
        self.block.remove_lines(self.lines)
    
    def replace(
            self,
            *strings: str,
            indent_lines: int|CodeLineGroup|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.block.replace_lines(
            self.lines,
            *strings,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
    
    def enclose(
            self,
            before: str,
            after: str,
            *,
            indent: int = None,
            prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.block.enclose_lines(
            lines = self.lines,
            before = before,
            after = after,
            indent = indent,
            prompt = prompt,
            plain = plain,
        )
    
    def highlight(self, pattern: str|Pattern = None) -> ContextManager[None]:
        if pattern is not None:
            return self.block.highlight_pattern(pattern, self.lines)
        else:
            return self.block.highlight_lines(self.lines)
    

def split_enclosure(prompt_pattern: str, string: str) -> tuple[list[str], list[str], str, int]:
    enclosure_pattern = re.compile(rf'^({prompt_pattern})(\s*)\{{\.\.\.\}}$')
    before: list[CodeLine] = []
    after: list[CodeLine] = []
    prompt: str = None
    indent: int = None
    lines = before
    for line in split_lines(string):
        match = enclosure_pattern.match(line)
        if match:
            prompt, whitespace = match.groups()
            indent = len(whitespace)
            lines = after
            continue
        lines.append(line)
    return before, after, prompt, indent


from .codeblock import CodeBlock