from manim import (
    UP,
    UL,
    UR,
    DOWN,
    LEFT,
    Group,
    Rectangle,
    Circle,
    Create,
    FadeIn,
    GrowFromCenter,
)

from ..codescene import CodeScene
from ..codeconfig import CodeConfig


class Window(CodeConfig.theme):
    font = 'Consolas'
    font_size = 22
    font_color = '#000000'
    line_gap = 0.25
    draw_window = False
    background_color = '#ffffff'
    window_color = '#ffffff'
    window_border_color = '#000000'
    window_border_width = 4
    window_padding = 0.25
    navbar_height = 0.5
    navbar_color = '#888888'
    controls_color = '#ffffff'
    z_range = 5

    @property
    def config(self) -> CodeConfig:
        return self.parent
    
    @property
    def horizontal_padding(self) -> float:
        return self.window_padding
    
    @property
    def top_padding(self) -> float:
        return self.navbar_height + self.window_padding
    
    def init(self, scene: CodeScene) -> None:
        super().init(scene)
        z_index *= self.z_range
        window = Rectangle(
            height = self.config.height,
            width = self.config.width,
            stroke_width = 0,
            fill_color = self.window_color,
            fill_opacity = 1,
        )
        overflow_top = Rectangle(
            width = self.config.width,
            height = 8,
            stroke_width = 0,
            fill_color = self.background_color,
            fill_opacity = 1,
        )
        overflow_top.z_index = z_index + 1
        overflow_top.next_to(window, UP, buff=0)
        overflow_bottom = overflow_top.copy()
        overflow_bottom.next_to(window, DOWN, buff=0)
        border = Rectangle(
            width = self.config.width,
            height = self.config.height,
            color = self.window_border_color,
            stroke_width = self.window_border_width,
        )
        border.z_index = z_index + 2
        border.align_to(window, UL)
        navbar = Rectangle(
            height = self.navbar_height,
            width = self.config.width,
            color = self.window_border_color,
            stroke_width = self.window_border_width,
            fill_color = self.navbar_color,
            fill_opacity = 1,
        )
        navbar.z_index = z_index + 3
        navbar.align_to(window, UL)
        button_size = self.navbar_height / 7
        button1 = Circle(
            radius = button_size,
            stroke_width = self.window_border_width,
            color = self.controls_color,
            fill_color = self.window_color,
            fill_opacity = 1,
        )
        button1.z_index = z_index + 4
        button2 = button1.copy()
        button3 = button1.copy()
        button1.align_to(navbar, UR).shift(DOWN * button_size * 2.5, LEFT * button_size * 3)
        button2.align_to(button1, UL).shift(LEFT * button_size * 4)
        button3.align_to(button2, UL).shift(LEFT * button_size * 4)
        controls = Group(border, navbar, button1, button2, button3)
        if animate:
            scene.play(Create(border), run_time=0.7)
            scene.play(FadeIn(window), FadeIn(navbar), run_time=0.3)
            scene.add(overflow_top, overflow_bottom)
            scene.play(GrowFromCenter(button3), run_time=0.2)
            scene.play(GrowFromCenter(button2), run_time=0.2)
            scene.play(GrowFromCenter(button1), run_time=0.2)
        else:
            scene.add(window, overflow_top, overflow_bottom, navbar, controls)