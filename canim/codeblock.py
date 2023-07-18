from __future__ import annotations

from manim import Text, UL, DOWN, LEFT, AddTextLetterByLetter


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
    
    def insert_line(self, text: str, index: int) -> CodeLine:
        line = CodeLine(self, text)
        self._lines.insert(index, line)
        self._animate_line_insertion(line, index)
        return line
    
    def prepend_line(self, text: str) -> CodeLine:
        return self.insert_line(text, 0)
    
    def append_line(self, text: str) -> CodeLine:
        return self.insert_line(text, len(self._lines))
    
    def _animate_line_insertion(self, line: CodeLine, index: int) -> None:
        mobject = Text(
            text = line.text,
            font = self.config.font,
            font_size = self.config.font_size,
        )
        if index == 0:
            mobject.move_to([self.x, self.y, 0], UL)
        else:
            prev_line = self._lines[index - 1]
            mobject.next_to(prev_line._mobject, DOWN, buff=self.config.line_gap)
            mobject.align_to(prev_line._mobject, LEFT)
        line._mobject = mobject
        self._scene.wait(self.config.delay_before)
        slide_down = []
        height_diff = mobject.height + self.config.line_gap
        for next_line in self._lines[index + 1:]:
            slide_down.append(next_line._mobject.animate.shift(height_diff * DOWN))
        if slide_down:
            self._scene.play(*slide_down, run_time=self.config.slide_speed)
        duration = len(line.text) * self.config.typing_speed
        self._scene.play(AddTextLetterByLetter(mobject), run_time=duration)
        self._scene.wait(self.config.delay_after)
        self._scene.next_section()


from .codeconfig import CodeConfig
from .codeline import CodeLine
from .codescene import CodeScene