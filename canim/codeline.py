from __future__ import annotations
from typing import Any, ContextManager, Pattern

import re

from manim import (
    UL,
    DOWN,
    RIGHT,
    Mobject,
    Group,
    FadeIn,
    FadeOut,
    AddTextLetterByLetter,
    ReplacementTransform,
)

from .utils import split_lines


class CodeLine:

    def __init__(
            self,
            block: CodeBlock,
            content: str,
            indent: int = None,
            prompt: str = None,
            plain: bool = None
    ):
        if indent is None:
            indent = 0
        if plain is None:
            plain = False
        self.block = block
        self.content = content
        self.indent = indent
        self.prompt = None
        if not plain:
            if block._syntax_highlighter:
                content = block._syntax_highlighter.highlight(content)
            if prompt:
                self.prompt = block._create_text(prompt)
        self.text = block._create_text(content)
        self._stash: dict[str, Any] = {}
    
    def __repr__(self):
        index = self.index
        return f'<line {index if index is not None else "-"}: {self.string}>'

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
    
    def __add__(self, other: CodeLine|CodeLineGroup) -> CodeLineGroup:
        if isinstance(other, CodeLine):
            return CodeLineGroup(self.block, [self, other])
        return CodeLineGroup(self.block, [self, *other.lines])
    
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
        prompt, whitespace, content = re.match(f'^({block.config.prompt_pattern})?(\s*)(.*)$', line).groups()
        return cls(
            block = block,
            content = content,
            prompt = prompt,
            indent = len(whitespace),
            plain = plain,
        )

    @property
    def string(self) -> str:
        output: list[str] = []
        if self.prompt:
            output.append(self.prompt.text)
        if self.indent:
            output.append(' ' * self.indent)
        output.append(self.content)
        return ''.join(output)
    
    @property
    def index(self) -> None|int:
        try:
            return self.block.lines.index(self)
        except ValueError:
            return None
        
    @property
    def top(self) -> float:
        return self.text.get_top()[1] + self.block._font_alignment.top_margin(self.content)
    
    @property
    def left(self) -> float:
        if self.prompt:
            mobject = self.prompt
        else:
            mobject = self.text
        return mobject.get_left()[0] - self.block._font_alignment.left_margin(mobject.text)
    
    @property
    def bottom(self) -> float:
        return self.top - self.block._font_alignment.height - self.block.theme.line_gap
    
    @property
    def right(self) -> float:
        return self.text.get_right()[0] + self.block._font_alignment.right_margin(self.text.text)

    @property
    def height(self) -> float:
        return self.top - self.bottom
    
    @property
    def width(self) -> float:
        return self.right - self.left
    
    @property
    def typing_duration(self) -> float:
        return len(self.content.replace(' ', '')) * self.block.config.typing_speed

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
        
    def remove(
            self,
            dedent_lines: int|CodeLineGroup|list[CodeLine] = None,
            dedent_level: int = None,
            dedent_prompt: str = None,
    ) -> None:
        self.block.remove_lines(
            lines = [self],
            dedent_lines = dedent_lines,
            dedent_level = dedent_level,
            dedent_prompt = dedent_prompt,
        )
    
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
        if self.prompt:
            prompt_top = top - self.block._font_alignment.top_margin(self.prompt.text)
            prompt_left = left + self.block._font_alignment.left_margin(self.prompt.text)
            self.prompt.move_to([prompt_left, prompt_top, 0], UL)
            text_top = top - self.block._font_alignment.top_margin(self.content)
            text_left = (
                self.prompt.get_right()[0]
                + self.block._font_alignment.right_margin(self.prompt.text)
                + self.block._font_alignment.space_width * (self.indent + 1)
                + self.block._font_alignment.left_margin(self.content)
            )
            self.text.move_to([text_left, text_top, 0], UL)
        else:
            text_top = top - self.block._font_alignment.top_margin(self.content)
            text_left = left + self.block._font_alignment.left_margin(self.content)
            self.text.move_to([text_left, text_top, 0], UL)

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
        if replace_with and self.prompt and replace_with.prompt and self.prompt.text == replace_with.prompt.text:
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
        if indent is None:
            indent = 0
        down = offset * DOWN
        right = self.block._font_alignment.space_width * indent * RIGHT
        self.block._add_transition(self.text.animate.shift(down + right))
        if self.prompt:
            if prompt and prompt != self.prompt.text:
                new_prompt = self.block._create_text(prompt)
                top = self.top - self.block._font_alignment.top_margin(prompt) - offset
                left = self.left + self.block._font_alignment.left_margin(prompt)
                new_prompt.move_to([left, top, 0], UL)
                self.block._add_transition(ReplacementTransform(self.prompt, new_prompt))
                self.prompt = new_prompt
            else:
                self.block._add_transition(self.prompt.animate.shift(down))
        self.indent += indent

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

    def __add__(self, other: CodeLine|CodeLineGroup) -> CodeLineGroup:
        if isinstance(other, CodeLine):
            return CodeLineGroup(self.block, [*self.lines, other])
        return CodeLineGroup(self.block, [*self.lines, *other.lines])
    
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
    
    def remove(
            self,
            dedent_lines: int|CodeLineGroup|list[CodeLine] = None,
            dedent_level: int = None,
            dedent_prompt: str = None,
    ) -> None:
        self.block.remove_lines(
            lines = self.lines,
            dedent_lines = dedent_lines,
            dedent_level = dedent_level,
            dedent_prompt = dedent_prompt,
        )
    
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
    

def split_enclosure(prompt_pattern: str, string: str) -> tuple[str, str, str, int]:
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
    return '\n'.join(before), '\n'.join(after), prompt, indent


from .codeblock import CodeBlock