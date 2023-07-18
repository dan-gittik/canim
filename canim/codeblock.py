from __future__ import annotations
from typing import ContextManager

import contextlib

from manim import (
    UL,
    UP,
    DOWN,
    LEFT,
    Mobject,
    Text,
    Animation,
    FadeOut,
    AddTextLetterByLetter,
)

from .utils import split_lines


class CodeBlock:
    
    def __init__(self, scene: CodeScene, x: float, y: float):
        self.x = x
        self.y = y
        self.lines = LineGroupSelector(self)
        self._scene = scene
        self._lines: list[CodeLine] = []
    
    def __repr__(self):
        return f'<code block at ({self.x}, {self.y})>'
    
    @property
    def config(self) -> CodeConfig:
        return self._scene.code_config
    
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
    
    @contextlib.contextmanager
    def _section(self) -> ContextManager[None]:
        self._scene.wait(self.config.delay_before)
        try:
            yield
        finally:
            self._scene.wait(self.config.delay_after)
            self._scene.next_section()
    
    def _animate_line_insertion(self, lines: list[CodeLine]) -> None:
        if not lines:
            return
        mobjects: list[Mobject] = []
        for line in lines:
            mobject = Text(
                text = line.text,
                font = self.config.font,
                font_size = self.config.font_size,
            )
            if line.index == 0:
                mobject.move_to([self.x, self.y, 0], UL)
            else:
                prev_line = self._lines[line.index - 1]
                mobject.next_to(prev_line._mobject, DOWN, buff=self.config.line_gap)
                mobject.align_to(prev_line._mobject, LEFT)
            line._mobject = mobject
            mobjects.append(mobject)
        with self._section():
            slide_down: list[Animation] = []
            height_diff = sum(mobject.height + self.config.line_gap for mobject in mobjects)
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
        with self._section():
            height_diff = 0
            effects: list[Animation] = []
            for index, line in enumerate(self._lines):
                if index in remove:
                    height_diff += line._mobject.height + self.config.line_gap
                    effects.append(FadeOut(line._mobject))
                elif height_diff:
                    effects.append(line._mobject.animate.shift(height_diff * UP))
            self._scene.play(*effects, run_time=self.config.slide_speed)


from .codeconfig import CodeConfig
from .codeline import CodeLine
from .codescene import CodeScene
from .linegroup import LineGroupSelector, LineGroup