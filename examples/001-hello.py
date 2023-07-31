from canim import code_animation
from manim import Scene, Text


@code_animation
def example(scene: Scene):
    scene.add(Text('Hello, world!'))
    scene.wait(1)