from __future__ import annotations

from manim import Scene


class CodeScene(Scene):

    code_config: CodeConfig = None

    def __repr__(self):
        return f'<code scene {self.__class__.__name__!r}>'

    def create_code_block(self, x: float, y: float) -> CodeBlock:
        return CodeBlock(self, x, y)


from .codeblock import CodeBlock
from .codeconfig import CodeConfig