from __future__ import annotations

from manim_voiceover import VoiceoverScene


class CodeScene(VoiceoverScene):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def __repr__(self):
        return f'<code scene {self.__class__.__name__!r}>'
    
    def __call__(
            self,
            x: float,
            y: float,
            font: str = None,
            font_size: int = None,
            line_gap: float = None,
            typing_speed: float = None,
            slide_speed: float = None,
            voiceover: bool = None,
    ) -> CodeBlock:
        config = CodeConfig(
            font = font,
            font_size = font_size,
            line_gap = line_gap,
            typing_speed = typing_speed,
            slide_speed = slide_speed,
            voiceover = voiceover,
        )
        return CodeBlock(self, x, y, config)


from .codeblock import CodeBlock
from .codeconfig import CodeConfig