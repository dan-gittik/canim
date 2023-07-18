from typing import Callable

import functools

from .codeconfig import CodeConfig
from .codescene import CodeScene


def code_animation(
        function: Callable = None,
        /,
        *,
        font: str = None,
        font_size: int = None,
        delay: float = None,
        delay_before: float = None,
        delay_after: float = None,
        typing_speed: float = None,
        slide_speed: float = None,
):
    if function is None:
        return functools.partial(code_animation,
            font = font,
            font_size = font_size,
            delay = delay,
            delay_before = delay_before,
            delay_after = delay_after,
            typing_speed = typing_speed,
            slide_speed = slide_speed,
        )
    return type(function.__name__, (CodeScene,), dict(
        construct = function,
        __module__ = function.__module__, # Required by manim to recognize that a class is a scene.
        code_config = CodeConfig(
            font = font,
            font_size = font_size,
            delay = delay,
            delay_before = delay_before,
            delay_after = delay_after,
            typing_speed = typing_speed,
            slide_speed = slide_speed,
        ),
    ))