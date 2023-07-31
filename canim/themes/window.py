from typing import Any

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
    animate = True
    font = 'Consolas'
    font_size = 20
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
    text_z_index = 2
    last_z_index = 7

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
        z_index = self.z_index * self.last_z_index
        self._draw_window(scene, z_index)
        self._draw_mask(scene, z_index)
        self._draw_navbar(scene, z_index)
        self._animate(scene)
    
    def _draw_window(self, scene: CodeScene, z_index: int) -> None:
        self._window = Rectangle(
            height = self.config.height,
            width = self.config.width,
            stroke_width = 0,
            fill_color = self.window_color,
            fill_opacity = 1,
        )
        self._window.z_index = z_index
        self._border = Rectangle(
            width = self.config.width,
            height = self.config.height,
            color = self.window_border_color,
            stroke_width = self.window_border_width,
        )
        self._border.z_index = self._window.z_index + 4
        self._border.align_to(self._window, UL)

    def _draw_mask(self, scene: CodeScene, z_index: int) -> None:
        self._overflow_top = Rectangle(
            width = self.config.width,
            height = 8,
            stroke_width = 0,
            fill_color = self.background_color,
            fill_opacity = 1,
        )
        self._overflow_top.z_index = z_index + 3
        self._overflow_top.next_to(self._border, UP, buff=0)
        self._overflow_bottom = self._overflow_top.copy()
        self._overflow_bottom.next_to(self._border, DOWN, buff=0)
    
    def _draw_navbar(self, scene: CodeScene, z_index: int):
        self._navbar = Rectangle(
            height = self.navbar_height,
            width = self.config.width,
            color = self.window_border_color,
            stroke_width = self.window_border_width,
            fill_color = self.navbar_color,
            fill_opacity = 1,
        )
        self._navbar.z_index = self._border.z_index + 1
        self._navbar.align_to(self._window, UL)
        button_size = self.navbar_height / 7
        self._button1 = Circle(
            radius = button_size,
            stroke_width = self.window_border_width,
            color = self.controls_color,
            fill_color = self.window_color,
            fill_opacity = 1,
        )
        self._button1.z_index = self._navbar.z_index + 1
        self._button2 = self._button1.copy()
        self._button3 = self._button1.copy()
        self._button1.align_to(self._navbar, UR).shift(DOWN * button_size * 2.5, LEFT * button_size * 3)
        self._button2.align_to(self._button1, UL).shift(LEFT * button_size * 4)
        self._button3.align_to(self._button2, UL).shift(LEFT * button_size * 4)
        self._controls = Group(self._border, self._navbar, self._button1, self._button2, self._button3)
    
    def _animate(self, scene: CodeScene) -> None:
        if self.animate:
            scene.play(Create(self._border), run_time=0.7)
            scene.play(FadeIn(self._window), FadeIn(self._navbar), run_time=0.3)
            scene.add(self._overflow_top, self._overflow_bottom)
            scene.play(GrowFromCenter(self._button3), run_time=0.2)
            scene.play(GrowFromCenter(self._button2), run_time=0.2)
            scene.play(GrowFromCenter(self._button1), run_time=0.2)
        else:
            scene.add(self._window, self._overflow_top, self._overflow_bottom, self._navbar, self._controls)