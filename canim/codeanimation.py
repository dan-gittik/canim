from typing import Callable

from .codescene import CodeScene


def code_animation(function: Callable) -> Callable:
    return type(function.__name__, (CodeScene,), dict(
        construct = function,
        __module__ = function.__module__, # Required by manim to recognize that a class is a scene.
    ))