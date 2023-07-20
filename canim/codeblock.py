from __future__ import annotations
from typing import Any, ContextManager

import contextlib
import re

from manim import (
    UP,
    UL,
    UR,
    DOWN,
    DL,
    DR,
    LEFT,
    RIGHT,
    Mobject,
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
        lines = []
        for string in strings:
            for text in split_lines(string):
                line = CodeLine(self, text)
                lines.append(line)
        self._lines[index:index] = lines
        self._animate_line_insertion(lines)
        return lines
    
    def prepend_lines(self, *strings: str) -> list[CodeLine]:
        return self.insert_lines(0, *strings)
    
    def append_lines(self, *strings: str) -> list[CodeLine]:
        return self.insert_lines(len(self._lines), *strings)
    
    def remove_lines(self, *lines: CodeLine) -> None:
        self._animate_line_removal(lines)
        for line in lines:
            self._lines.remove(line)
    
    def _animate_line_insertion(self, lines: list[CodeLine]) -> None:
        if not lines:
            return
        mobjects: list[Mobject] = []
        print(self.style.font_size)
        for line in lines:
            mobject = Text(
                text = line.text,
                font = self.style.font,
                font_size = self.style.font_size,
                color = self.style.font_color,
            )
            if line.index == 0:
                x = -(self.config.width / 2) + self.config.style.x_padding
                y = self.config.height / 2 - self.config.style.y_padding
                mobject.move_to([x, y, 0], UL)
            else:
                prev_line = self._lines[line.index - 1]
                mobject.next_to(prev_line._mobject, DOWN, buff=self.style.line_gap)
                mobject.align_to(prev_line._mobject, LEFT)
            line._mobject = mobject
            mobjects.append(mobject)
        slide_down: list[Animation] = []
        height_diff = sum(mobject.height + self.style.line_gap for mobject in mobjects)
        for next_line in self._lines[line.index + 1:]:
            slide_down.append(next_line._mobject.animate.shift(height_diff * DOWN))
        if slide_down:
            self._scene.play(*slide_down, run_time=self.config.slide_speed)
        for line, mobject in zip(lines, mobjects):
            duration = len(line.text) * self.config.typing_speed
            self._scene.play(AddTextLetterByLetter(mobject), run_time=duration)

    def _animate_line_removal(self, lines: list[CodeLine]) -> None:
        if not lines:
            return
        remove = {line.index for line in lines}
        height_diff = 0
        effects: list[Animation] = []
        for index, line in enumerate(self._lines):
            if index in remove:
                height_diff += line._mobject.height + self.style.line_gap
                effects.append(FadeOut(line._mobject))
            elif height_diff:
                effects.append(line._mobject.animate.shift(height_diff * UP))
        self._scene.play(*effects, run_time=self.config.slide_speed)


from .codeconfig import CodeConfig
from .codeline import CodeLine, CodeLineGroup
from .codescene import CodeScene