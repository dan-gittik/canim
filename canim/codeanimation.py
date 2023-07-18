from typing import Callable

from manim import Scene


def code_animation(function: Callable) -> Callable:
    return type(function.__name__, (Scene,), dict(
        construct = function,
        __module__ = function.__module__, # Required by manim to recognize that a class is a scene.
    ))