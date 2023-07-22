from __future__ import annotations
from typing import Any, ContextManager, Pattern

import contextlib
import re

from manim import (
    UP,
    UL,
    DOWN,
    LEFT,
    RIGHT,
    MarkupText,
    Rectangle,
    Animation,
    FadeIn,
    FadeOut,
    LaggedStart,
    AddTextLetterByLetter,
)
from manim_voiceover import VoiceoverTracker
from manim_voiceover.services.recorder import RecorderService

from .utils import split_lines


bookmark_regex = re.compile(r'\{(.*?)\}')


class CodeBlock:

    
    def __init__(
            self,
            scene: CodeScene,
            config: CodeConfig,
            *,
            animate: bool = None,
            z_index: int = None,
            language: str = None,
    ):
        if z_index is None:
            z_index = 0
        self.config = config
        self._scene = scene
        self._syntax_highlighter = SyntaxHighligher(language, config.style.syntax) if language else None
        self._lines: list[CodeLine] = []
        self._stash: dict[str, Any] = {}
        if self.config.voiceover:
            self._scene.set_speech_service(RecorderService())
        if self.style.background_color:
            self._scene.camera.background_color = self.style.background_color
        self.config.style.initialize(self._scene, animate=animate, z_index=z_index)
        self.z_index = z_index + self.config.style.z_range
    
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
    
    def __call__(self, **stash: dict[str, Any]) -> CodeBlock:
        self._stash = stash
        return self
    
    def __neg__(self) -> CodeBlock:
        self.clear()
        return self
    
    def __rshift__(self, *strings: str) -> list[CodeLine]:
        lines = self.append_lines(*strings, **self._stash)
        self._stash.clear()
        return lines
    
    def __lshift__(self, *strings: str) -> list[CodeLine]:
        lines = self.prepend_lines(*strings, **self._stash)
        self._stash.clear()
        return lines
    
    def __matmul__(self, bookmark: Any) -> None:
        self._scene.wait_until_bookmark(str(bookmark))
    
    def __irshift__(self, *strings: str) -> CodeBlock:
        self.append_lines(*strings, raw=True, at_once=True)
        return self
    
    @contextlib.contextmanager
    def voiceover(self, text: str) -> ContextManager[VoiceoverTracker]:
        text = bookmark_regex.sub(r'<bookmark mark="\1" />', text)
        with self._scene.voiceover(text=text) as tracker:
            yield tracker
        
    @property
    def style(self) -> CodeConfig.style:
        return self.config.style

    def insert_lines(
            self,
            index: int,
            *strings: str,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        if not strings:
            return
        if index > len(self._lines):
            index = len(self._lines)
        lines = self._create_lines(index, strings, raw=raw)
        scroll = self._find_scroll_for(lines[0], lines[-1])
        self._animate_slide(scroll)
        for line in lines:
            line._mobject.shift(scroll * UP)
        height_diff = -self._height(*lines)
        self._animate_slide(height_diff, self._lines[index:])
        self._animate_insert(lines, at_once=at_once)
        self._insert(index, lines)
        return lines
    
    def prepend_lines(
            self,
            *strings: str,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        return self.insert_lines(0, *strings,
            raw = raw,
            at_once = at_once,
        )
    
    def append_lines(
            self,
            *strings: str,
            raw: bool = None,
            at_once: bool = None
    ) -> list[CodeLine]:
        return self.insert_lines(len(self._lines), *strings,
            raw = raw,
            at_once = at_once,
        )
    
    def remove_lines(self, lines: list[CodeLine]) -> None:
        if not lines:
            return
        self._animate_remove(lines)
        self._delete(lines)
    
    def replace_lines(
            self,
            lines: list[CodeLine],
            *strings: str,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        if not lines or not strings:
            return
        index = lines[0].index
        new_lines = self._create_lines(index, strings, raw=raw)
        scroll = self._find_scroll_for(new_lines[0], new_lines[-1])
        self._animate_slide(scroll)
        for line in lines:
            line._mobject.shift(scroll * UP)
        self._animate_replace(index, lines, new_lines)
        self._animate_insert(new_lines, at_once=at_once)
        self._insert(index, new_lines)
        self._delete(lines)
        return new_lines
    
    def enclose_lines(
            self,
            lines: list[CodeLine],
            before: str,
            after: str,
            indent: int = None,
            raw: bool = None,
            at_once: bool = None,
    ) -> list[CodeLine]:
        if not lines:
            return
        before_index = lines[0].index
        before_lines = self._create_lines(before_index, before, raw=raw)
        after_index = lines[-1].index + 1
        after_lines = self._create_lines(after_index, after, raw=raw)
        scroll = self._find_scroll_for(before_lines[0], after_lines[-1])
        self._animate_slide(scroll)
        for line in before_lines:
            line._mobject.shift(scroll * UP)
        for line in after_lines:
            line._mobject.shift(scroll * UP)
        self._animate_enclose(before_index, after_index, before_lines, after_lines, indent=indent)
        new_lines = [*before_lines, *after_lines]
        self._animate_insert(new_lines, at_once=at_once)
        self._insert(before_index, before_lines)
        self._insert(after_index, after_lines)
        return new_lines
    
    def scroll_into_view(self, first_line: CodeLine, last_line: CodeLine = None) -> None:
        if last_line is None:
            last_line = first_line
        scroll = self._find_scroll_for(first_line, last_line)
        self._animate_slide(scroll)
    
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
        
    def clear(self) -> None:
        self.remove_lines(self._lines)
        
    def _height(self, *lines: CodeLine) -> float:
        return sum(line._mobject.height + self.style.line_gap for line in lines)
    
    def _insert(self, index: int, lines: list[CodeLine]) -> None:
        self._lines[index:index] = lines

    def _delete(self, lines: list[CodeLine]) -> None:
        self._lines = [line for line in self._lines if line not in lines]

    def _create_text(self, text: str, raw: bool = None) -> MarkupText:
        if self._syntax_highlighter and not raw:
            text = self._syntax_highlighter.highlight(text)
        mobject = MarkupText(
            text = text,
            font = self.style.font,
            font_size = self.style.font_size,
            color = self.style.font_color,
        )
        mobject.z_index = self.z_index + 2
        return mobject

    def _create_lines(self, index: int, strings: list[str], raw: bool = None) -> list[CodeLine]:
        lines: list[CodeLine] = []
        for string in strings:
            for text in split_lines(string):
                line = CodeLine(self, text)
                lines.append(line)
        prev_line: CodeLine = None
        for line_index, line in enumerate(lines, index):
            mobject = self._create_text(line.text, raw=raw)
            if line_index == 0:
                if not self._lines:
                    x = -(self.config.width / 2) + self.style.horizontal_padding
                    y = self.config.height / 2 - self.style.top_padding
                    mobject.move_to([x, y, 0], UL)
                else:
                    mobject.align_to(self._lines[0]._mobject, UL)
            else:
                if prev_line is None:
                    prev_line = self._lines[line_index - 1]
                mobject.next_to(prev_line._mobject, DOWN, buff=self.style.line_gap)
                mobject.align_to(prev_line._mobject, LEFT)
            line._mobject = mobject
            prev_line = line
        return lines
    
    def _find_scroll_for(self, first_line: CodeLine, last_line: CodeLine = None) -> float:
        threshold = first_line._mobject.height / 2
        upper_limit = self.config.height / 2 - self.style.top_padding
        top = first_line._mobject.get_top()[1]
        if top > upper_limit + threshold:
            return -(top - upper_limit)
        lower_limit = - self.config.height / 2 + self.style.bottom_padding
        bottom = last_line._mobject.get_bottom()[1] - self.style.line_gap
        if bottom < lower_limit - threshold:
            return lower_limit - bottom
        return 0

    def _animate_insert(self, lines: list[CodeLine], at_once: bool = None) -> None:
        if not lines:
            return
        if at_once:
            animation: list[Animation] = []
            for line in lines:
                animation.append(FadeIn(line._mobject))
            self._scene.play(*animation, run_time=self.config.transition_speed)
        else:
            for line in lines:
                duration = len(line.text.replace(' ', '')) * self.config.typing_speed
                self._scene.play(AddTextLetterByLetter(line._mobject), run_time=duration)

    def _animate_remove(self, lines: list[CodeLine]) -> None:
        height_diff = 0
        animation: list[Animation] = []
        for line in self._lines:
            if line in lines:
                height_diff += self._height(line)
                animation.append(FadeOut(line._mobject))
            elif height_diff:
                animation.append(line._mobject.animate.shift(height_diff * UP))
        if animation:
            self._scene.play(*animation, run_time=self.config.transition_speed)

    def _animate_replace(self, index: int, old_lines: list[CodeLine], new_lines: list[CodeLine]) -> None:
        height_diff = -self._height(*new_lines)
        animation: list[Animation] = []
        for line in self._lines[index:]:
            if line in old_lines:
                height_diff += self._height(line)
                animation.append(FadeOut(line._mobject))
            elif height_diff:
                animation.append(line._mobject.animate.shift(height_diff * UP))
        if animation:
            self._scene.play(*animation, run_time=self.config.transition_speed)
    
    def _animate_enclose(
            self,
            before_index: int,
            after_index: int,
            before_lines: list[CodeLine],
            after_lines: list[CodeLine],
            indent: int = None,
    ):
        height_diff = -self._height(*before_lines)
        animation: list[Animation] = []
        for line in self._lines[before_index:after_index]:
            indent_diff = line._mobject.width / len(line.text) * indent if indent else 0
            if height_diff or indent_diff:
                animation.append(line._mobject.animate.shift(height_diff * UP + indent_diff * RIGHT))
        for line in after_lines:
            line._mobject.shift(height_diff * UP)
        height_diff -= self._height(*after_lines)
        for line in self._lines[after_index:]:
            if height_diff:
                animation.append(line._mobject.animate.shift(height_diff * UP))
        if animation:
            self._scene.play(*animation, run_time=self.config.transition_speed)
 
    def _animate_slide(self, slide: float, lines: list[CodeLine] = None) -> None:
        if lines is None:
            lines = self._lines
        if not slide or not lines or not self._lines:
            return
        animation: list[Animation] = []
        for line in lines:
            animation.append(line._mobject.animate.shift(slide * UP))
        if animation:
            self._scene.play(*animation, run_time=self.config.transition_speed)

    def _animate_opacity(self, opacity: float, lines: list[CodeLine] = None) -> None:
        if not lines:
            lines = self._lines
        animation: list[Animation] = []
        for line in lines:
            animation.append(line._mobject.animate.set_opacity(opacity))
        if animation:
            self._scene.play(*animation, run_time=self.config.transition_speed)
    
    @contextlib.contextmanager
    def _animate_highlights(self, pattern: Pattern, lines: list[CodeLine]) -> ContextManager[None]:
        appear: list[Animation] = []
        disappear: list[Animation] = []
        for line in lines:
            char_width = line._mobject.width / len(line.text)
            for match in pattern.finditer(line.text):
                start, end = match.start(), match.end()
                highlight = Rectangle(
                    height = line._mobject.height + self.style.highlight_padding,
                    width = 0.01,
                    fill_color = self.style.highlight_color,
                    fill_opacity = 1,
                )
                highlight.align_to(line._mobject, UL)
                highlight.shift((start - 0.5) * char_width * RIGHT)
                highlight.shift(self.style.highlight_padding / 2 * UP)
                self._scene.add(highlight)
                appear.append(highlight.animate.stretch_to_fit_width((end - start + 1) * char_width, about_edge=LEFT))
                disappear.append(FadeOut(highlight))
        if not appear:
            return
        self._scene.play(LaggedStart(*appear, lag_ratio=0.2, run_time=self.config.transition_speed))
        try:
            yield
        finally:
            self._scene.play(*disappear, run_time=self.config.transition_speed)


from .codeconfig import CodeConfig
from .codeline import CodeLine, CodeLineGroup
from .codescene import CodeScene
from .syntaxhighlighter import SyntaxHighligher