from __future__ import annotations
from typing import Any

from manim_voiceover import VoiceoverScene


class CodeScene(VoiceoverScene):

    default_animate = False

    def __repr__(self):
        return f'<code scene {self.__class__.__name__!r}>'
    
    def code(
            self,
            config_obj: CodeConfig = None,
            /,
            *,
            animate: bool = None,
            language: str = None,
            **config: Any,
    ) -> CodeBlock:
        if config_obj is None:
            config_obj = CodeConfig(**config)
        if animate is None:
            animate = self.default_animate
        return CodeBlock(self, config_obj, animate=animate, language=language)


from .codeblock import CodeBlock
from .codeconfig import CodeConfig