from __future__ import annotations
from typing import Any, ContextManager, Pattern

import contextlib
from itertools import zip_longest
import re

from manim import (
    UP,
    UL,
    LEFT,
    RIGHT,
    MarkupText,
    Rectangle,
    Animation,
    FadeOut,
    LaggedStart,
)
from manim_voiceover import VoiceoverTracker
from manim_voiceover.services.recorder import RecorderService

from .utils import split_lines


bookmark_regex = re.compile(r'\{(.*?)\}')


class CodeBlock:

    def __init__(self, scene: CodeScene, config: CodeConfig):
        self.scene = scene
        self.config = config
        self.lines: list[CodeLine] = []
        self._stash: dict[str, Any] = {}
        self._transitions: list[Animation] = []
        if config.language:
            self._syntax_highlighter = SyntaxHighligher(config.language, config.theme.syntax)
        else:
            self._syntax_highlighter = None
        self._font_alignment = FontAlignment(config.theme.font, config.theme.font_size)
        if self.config.voiceover:
            self.scene.set_speech_service(RecorderService())
        self.config.theme.init(self.scene)
    
    def __repr__(self):
        return f'<code block: {self.config}>'

    def __getitem__(self, selector: int|slice|tuple[int|slice]) -> CodeLineGroup:
        if not isinstance(selector, tuple):
            selector = selector,
        lines = []
        for index in selector:
            if isinstance(index, int):
                lines.append(self._lines[index])
            else:
                lines.extend(self._lines[index])
        return CodeLineGroup(self, lines)
    
    def __call__(self, **stash: Any) -> CodeBlock:
        self._stash = stash
        return self
    
    def __neg__(self) -> CodeBlock:
        self.clear(**self._stash)
        self._stash.clear()
        return self
    
    def __rshift__(self, string: str) -> list[CodeLine]:
        lines = self.append_lines(string, **self._stash)
        self._stash.clear()
        return lines
    
    def __lshift__(self, string: str) -> list[CodeLine]:
        lines = self.prepend_lines(string, **self._stash)
        self._stash.clear()
        return lines
    
    def __matmul__(self, bookmark: Any) -> CodeBlock:
        self.scene.wait_until_bookmark(str(bookmark))
        return self
    
    def __irshift__(self, string: str) -> CodeBlock:
        self.append_lines(string, plain=True)
        return self
    
    @contextlib.contextmanager
    def voiceover(self, text: str) -> ContextManager[VoiceoverTracker]:
        text = bookmark_regex.sub(r'<bookmark mark="\1" />', text)
        with self.scene.voiceover(text=text) as tracker:
            yield tracker
        
    @property
    def theme(self) -> CodeConfig.theme:
        return self.config.theme
    
    @property
    def top(self) -> float:
        return self.config.height / 2 - self.theme.top_padding
    
    @property
    def bottom(self) -> float:
        return -self.config.height / 2 + self.theme.bottom_padding
    
    @property
    def left(self):
        return -self.config.width / 2 + self.theme.horizontal_padding

    def scroll_into_view(self, first_line: CodeLine, last_line: CodeLine = None) -> None:
        self._animate_scroll_to_fit(first_line, last_line)

    def insert_lines(
            self,
            index: int,
            *strings: str,
            indent_lines: int|CodeLineGroup|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        lines = self._create_lines(*strings, plain=plain)
        if not lines:
            return
        if index < 0:
            index = 0
        if index > len(self.lines):
            index = len(self.lines)
        if isinstance(indent_lines, int):
            indent_lines = self.lines[index:index + indent_lines]
        elif isinstance(indent_lines, CodeLineGroup):
            indent_lines = indent_lines.lines
        self._animate_insert(
            insertions = {index: lines},
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
        self._insert(index, lines)
        return lines

    def prepend_lines(
            self,
            *strings: str,
            indent_lines: int|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.insert_lines(
            0,
            *strings,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
    
    def append_lines(
            self,
            *strings: str,
            indent_lines: int|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.insert_lines(
            len(self.lines),
            *strings,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
    
    def remove_lines(self, lines: list[CodeLine]) -> None:
        if not lines:
            return
        self._animate_remove(lines)
        self._remove(lines)
    
    def clear(self) -> None:
        self.remove_lines(self.lines)
    
    def replace_lines(
            self,
            lines: list[CodeLine],
            *strings: str,
            indent_lines: int|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        new_lines = self._create_lines(*strings, plain=plain)
        if not lines or not new_lines:
            return
        index = lines[0].index
        self._animate_insert(
            insertions = {index: new_lines},
            replace_lines = lines,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
        self._insert(index, new_lines)
        self._remove(lines)
        return new_lines
    
    def enclose_lines(
            self,
            lines: list[CodeLine],
            before: str,
            after: str,
            *,
            indent: int = None,
            prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        if not lines:
            return
        before_index = lines[0].index
        before_lines = self._create_lines(before, plain=plain)
        after_index = lines[-1].index + 1
        after_lines = self._create_lines(after, plain=plain)
        new_lines = [*before_lines, *after_lines]
        self._animate_insert(
            insertions = {before_index: before_lines, after_index: after_lines},
            indent_lines = self.lines[before_index:after_index],
            indent_level = indent,
            indent_prompt = prompt,
            plain = plain,
        )
        self._insert(before_index, before_lines)
        self._insert(after_index, after_lines)
        return new_lines
    
    @contextlib.contextmanager
    def highlight_lines(self, lines: list[CodeLine]) -> None:
        if not lines:
            return
        self.scroll_into_view(lines[0], lines[-1])
        other_lines = [line for line in self._lines if line not in lines]
        if other_lines:
            self._animate_opacity(self.style.dimmed_opacity, other_lines)
        try:
            yield
        finally:
            self._animate_opacity(1, other_lines)
    
    @contextlib.contextmanager
    def highlight_pattern(self, pattern: str|Pattern, lines: list[CodeLine] = None) -> None:
        if not lines:
            lines = self._lines
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        with self._animate_highlights(pattern, lines):
            yield
        
    def _add_transition(self, transition: Animation) -> None:
        self._transitions.append(transition)
    
    def _play_transitions(self, lag=None) -> None:
        if not self._transitions:
            return
        if self.config.animation:
            run_time = self.config.transition_speed
        else:
            run_time = 0
        if lag:
            self.scene.play(LaggedStart(*self._transitions, lag_ratio=lag, run_time=run_time))
        else:
            self.scene.play(*self._transitions, run_time=run_time)
        self._transitions.clear()
        
    def _insert(self, index: int, lines: list[CodeLine]) -> None:
        self.lines[index:index] = lines

    def _remove(self, lines: list[CodeLine]) -> None:
        self.lines = [line for line in self.lines if line not in lines]
    
    def _create_text(self, text: str) -> MarkupText:
        return MarkupText(
            text = text,
            font = self.theme.font,
            font_size = self.theme.font_size,
            color = self.theme.font_color,
        )

    def _create_lines(self, *strings: str, plain: bool = None) -> list[CodeLine]:
        lines: list[CodeLine] = None
        for string in strings:
            for line in split_lines(string):
                lines.append(CodeLine.parse(self, line, plain=plain))
        return lines
    
    def _position_lines(self, lines: list[CodeLine], index: int, offset: float) -> None:
        prev_line: CodeLine = None
        for line_index, line in enumerate(lines, index):
            if line_index == 0:
                line._position(self.top + offset, self.left)
            else:
                if prev_line is None:
                    prev_line = self.lines[line_index - 1]
                line._position(prev_line.bottom + offset, prev_line.left)
            prev_line = line
  
    def _animate_scroll_to_fit(self, first_line: CodeLine, last_line: CodeLine = None) -> float:
        if last_line is None:
            last_line = first_line
        threshold = first_line.height / 2
        if first_line.top > self.top + threshold:
            offset = first_line.top - self.top
        elif last_line.bottom < self.bottom - threshold:
            offset = -(self.bottom - last_line.bottom)
        else:
            offset = 0
        self._animate_slide(offset)
        return offset

    def _animate_slide(self, offset: float, lines: list[CodeLine] = None) -> None:
        if lines is None:
            lines = self.lines
        if not offset or not lines:
            return
        for line in lines:
            line._animate_slide(offset)
        self._play_transitions()

    def _animate_insert(
            self,
            insertions: dict[int, list[CodeLine]],
            replace_lines: list[CodeLine] = None,
            indent_lines: list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> None:
        if replace_lines is None:
            replace_lines = []
        offset = 0.0
        offsets: dict[int, float] = {}
        new_lines: list[CodeLine] = []
        first_index: int = None
        for index, lines in sorted(insertions.items()):
            self._position_lines(lines, index, offset)
            new_lines.extend(lines)
            for old_line, new_line in zip_longest(replace_lines, lines):
                if old_line and new_line:
                    old_line._animate_remove(replace_with=new_line)
                elif old_line:
                    old_line._animate_remove()
                    offset -= old_line.height
                elif new_line:
                    offset += new_line.height
            offsets[index] = offset
            if first_index is None:
                first_index = index
                offset = self._animate_scroll_to_fit(lines[0], lines[-1])
                for line in lines:
                    line._slide(offset)
        offset = 0.0
        for index, line in enumerate(self.lines[first_index:], first_index):
            if index in offsets:
                offset = offsets[index]
            if line in indent_lines:
                indent, prompt = indent_level, indent_prompt
            else:
                indent, prompt = None, None
            line._animate_slide(offset, indent=indent, prompt=prompt)
        self._play_transitions()
        for line in new_lines:
            line._animate_insert(plain=plain)
        self._play_transitions()
    
    def _animate_remove(self, lines: list[CodeLine]) -> None:
        offset = 0.0
        for line in self.lines:
            if line in lines:
                offset -= line.height
                line._animate_remove()
            elif offset:
                line._animate_slide(offset)
        self._play_transitions()

    def _animate_opacity(self, opacity: float, lines: list[CodeLine] = None) -> None:
        if not lines:
            lines = self.lines
        for line in lines:
            line._animate_opacity(opacity)
        self._play_transitions()
    
    @contextlib.contextmanager
    def _animate_highlights(self, pattern: Pattern, lines: list[CodeLine]) -> ContextManager[None]:
        highlights: list[Rectangle] = []
        for line in lines:
            char_width = line.width / len(line.string)
            for match in pattern.finditer(line.string):
                start, end = match.start(), match.end()
                highlight = Rectangle(
                    height = line.height + self.theme.highlight_padding,
                    width = 0.01,
                    fill_color = self.theme.highlight_color,
                    fill_opacity = 1,
                )
                highlight.move_to([line.top, line.left, 0], UL)
                highlight.shift((start - 0.5) * char_width * RIGHT)
                highlight.shift(self.theme.highlight_padding / 2 * UP)
                self.scene.add(highlight)
                self._add_transition(highlight.animate.stretch_to_fit_width((end - start + 1) * char_width, about_edge=LEFT))
                highlights.append(highlight)
        self._play_transitions(lag=0.2)
        try:
            yield
        finally:
            for highlight in highlights:
                self._add_transition(FadeOut(highlight))
            self._play_transitions()


from .codeconfig import CodeConfig
from .codeline import CodeLine, CodeLineGroup
from .codescene import CodeScene
from .fontalignment import FontAlignment
from .syntaxhighlighting import SyntaxHighligher