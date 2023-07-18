from __future__ import annotations

from manim import Text, UL, DOWN, LEFT, AddTextLetterByLetter, Mobject

from .utils import split_lines


class CodeBlock:
    
    def __init__(self, scene: CodeScene, x: float, y: float):
        self.x = x
        self.y = y
        self._scene = scene
        self._lines: list[CodeLine] = []
    
    def __repr__(self):
        return f'<code block at ({self.x}, {self.y})>'
    
    @property
    def config(self) -> CodeConfig:
        return self._scene.code_config
    
    def insert_line(self, string: str, index: int) -> CodeLine|list[CodeLine]:
        lines = [CodeLine(self, text) for text in split_lines(string)]
        self._lines[index:index] = lines
        self._animate_line_insertion(lines)
        if len(lines) == 1:
            return lines[0]
        return lines
    
    def prepend_line(self, string: str) -> CodeLine|list[CodeLine]:
        return self.insert_line(string, 0)
    
    def append_line(self, string: str) -> CodeLine|list[CodeLine]:
        return self.insert_line(string, len(self._lines))
    
    def _animate_line_insertion(self, lines: list[CodeLine]) -> None:
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
        self._scene.wait(self.config.delay_before)
        slide_down = []
        height_diff = sum(mobject.height + self.config.line_gap for mobject in mobjects)
        for next_line in self._lines[line.index + 1:]:
            slide_down.append(next_line._mobject.animate.shift(height_diff * DOWN))
        if slide_down:
            self._scene.play(*slide_down, run_time=self.config.slide_speed)
        for line, mobject in zip(lines, mobjects):
            duration = len(line.text) * self.config.typing_speed
            self._scene.play(AddTextLetterByLetter(mobject), run_time=duration)
        self._scene.wait(self.config.delay_after)
        self._scene.next_section()


from .codeconfig import CodeConfig
from .codeline import CodeLine
from .codescene import CodeScene