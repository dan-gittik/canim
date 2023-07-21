from __future__ import annotations
from typing import Any, ContextManager

import contextlib
import re

from manim import (
    UP,
    UL,
    DOWN,
    LEFT,
    Text,
    Animation,
    FadeOut,
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
    ):
        self.config = config
        self._scene = scene
        self._lines: list[CodeLine] = []
        if self.config.voiceover:
            self._scene.set_speech_service(RecorderService())
        if self.style.background_color:
            self._scene.camera.background_color = self.style.background_color
        self.config.style.initialize(self._scene, animate=animate)
    
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
    
    def __rshift__(self, *strings: str) -> list[CodeLine]:
        return self.append_lines(*strings)
    
    def __lshift__(self, *strings: str) -> list[CodeLine]:
        return self.prepend_lines(*strings)
    
    def __matmul__(self, bookmark: Any) -> None:
        self._scene.wait_until_bookmark(str(bookmark))
    
    @contextlib.contextmanager
    def voiceover(self, text: str) -> ContextManager[VoiceoverTracker]:
        text = bookmark_regex.sub(r'<bookmark mark="\1" />', text)
        with self._scene.voiceover(text=text) as tracker:
            yield tracker
        
    @property
    def style(self) -> CodeConfig.style:
        return self.config.style

    def insert_lines(self, index: int, *strings: str) -> list[CodeLine]:
        if not strings:
            return
        if index > len(self._lines):
            index = len(self._lines)
        lines = self._create_lines(index, strings)
        scroll = self._find_scroll_for(lines[0], lines[-1])
        self._animate_slide(scroll)
        for line in lines:
            line._mobject.shift(scroll * UP)
        height_diff = -self._height(*lines)
        self._animate_slide(height_diff, self._lines[index:])
        self._animate_typing(lines)
        self._insert(index, lines)
        return lines
    
    def prepend_lines(self, *strings: str) -> list[CodeLine]:
        return self.insert_lines(0, *strings)
    
    def append_lines(self, *strings: str) -> list[CodeLine]:
        return self.insert_lines(len(self._lines), *strings)
    
    def remove_lines(self, lines: list[CodeLine]) -> None:
        if not lines:
            return
        self._animate_remove(lines)
        self._delete(lines)
    
    def replace_lines(self, lines: list[CodeLine], *strings: str) -> None:
        if not lines or not strings:
            return
        index = lines[0].index
        new_lines = self._create_lines(index, strings)
        scroll = self._find_scroll_for(new_lines[0], new_lines[-1])
        self._animate_slide(scroll)
        for line in lines:
            line._mobject.shift(scroll * UP)
        self._animate_replace(index, lines, new_lines)
        self._animate_typing(new_lines)
        self._insert(index, new_lines)
        self._delete(lines)
        return new_lines

    def scroll_into_view(self, first_line: CodeLine, last_line: CodeLine = None) -> None:
        if last_line is None:
            last_line = first_line
        scroll = self._find_scroll_for(first_line, last_line)
        self._animate_slide(scroll)
        
    def _height(self, *lines: CodeLine) -> float:
        return sum(line._mobject.height + self.style.line_gap for line in lines)
    
    def _insert(self, index: int, lines: list[CodeLine]) -> None:
        self._lines[index:index] = lines

    def _delete(self, lines: list[CodeLine]) -> None:
        for line in lines:
            self._lines.remove(line)

    def _create_lines(self, index: int, strings: list[str]) -> list[CodeLine]:
        lines: list[CodeLine] = []
        for string in strings:
            for text in split_lines(string):
                line = CodeLine(self, text)
                lines.append(line)
        prev_line: CodeLine = None
        for line_index, line in enumerate(lines, index):
            mobject = Text(
                text = line.text,
                font = self.style.font,
                font_size = self.style.font_size,
                color = self.style.font_color,
            )
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
        top = first_line._mobject.get_y() + first_line._mobject.height / 2
        if top > upper_limit + threshold:
            return -(top - upper_limit)
        lower_limit = - self.config.height / 2 + self.style.bottom_padding
        bottom = last_line._mobject.get_y() - last_line._mobject.height / 2 - self.style.line_gap
        if bottom < lower_limit - threshold:
            return lower_limit - bottom
        return 0

    def _animate_typing(self, lines: list[CodeLine]) -> None:
        for line in lines:
            duration = len(line.text) * self.config.typing_speed
            self._scene.play(AddTextLetterByLetter(line._mobject), run_time=duration)

    def _animate_slide(self, slide: float, lines: list[CodeLine] = None) -> None:
        if lines is None:
            lines = self._lines
        if not slide or not lines or not self._lines:
            return
        animation: list[Animation] = []
        for line in lines:
            animation.append(line._mobject.animate.shift(slide * UP))
        if animation:
            self._scene.play(*animation, run_time=self.config.slide_speed)

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
            self._scene.play(*animation, run_time=self.config.slide_speed)

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
            self._scene.play(*animation, run_time=self.config.slide_speed)


from .codeconfig import CodeConfig
from .codeline import CodeLine, CodeLineGroup
from .codescene import CodeScene