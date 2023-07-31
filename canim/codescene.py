from __future__ import annotations
from typing import Any, Callable

from manim_voiceover import VoiceoverScene


def code_animation(function: Callable) -> Callable:
    return type(function.__name__, (CodeScene,), dict(
        construct = function,
        __module__ = function.__module__, # Required by manim to recognize that a class is a scene.
    ))


class CodeScene(VoiceoverScene):

    def __repr__(self):
        return f'<code scene {self.__class__.__name__!r}>'
    
    def code(self, config_obj: CodeConfig = None, **config: Any) -> CodeBlock:
        if config_obj is None:
            config_obj = CodeConfig(**config)
        return CodeBlock(self, config_obj)


from .codeblock import CodeBlock
from .codeconfig import CodeConfig