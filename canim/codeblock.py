from __future__ import annotations

from manim import Text, UL, DOWN, LEFT


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
    
    def append_line(self, text: str) -> CodeLine:
        line = CodeLine(self, text)
        self._lines.append(line)
        self._animate_line_insertion(line)
        return line
    
    def _animate_line_insertion(self, line: CodeLine) -> None:
        mobject = Text(
            text = line.text,
            font = self.config.font,
            font_size = self.config.font_size,
        )
        if line.index == 0:
            mobject.move_to([self.x, self.y, 0], UL)
        else:
            prev = self._lines[line.index - 1]
            mobject.next_to(prev._mobject, DOWN, buff=self.config.line_gap)
            mobject.align_to(prev._mobject, LEFT)
        line._mobject = mobject
        self._scene.wait(self.config.delay_before)
        self._scene.add(mobject)
        self._scene.wait(self.config.delay_after)
        self._scene.next_section()


from .codeconfig import CodeConfig
from .codeline import CodeLine
from .codescene import CodeScene