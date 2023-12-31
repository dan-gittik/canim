from manim import (
    UL,
    DL,
)

from .window import Window
from ..codescene import CodeScene
from ..codeconfig import CodeConfig


class Bauhaus(Window):
    font = 'DM Mono'
    paragraph_font = 'Josefin Sans'
    background_color = '#f0e2c8'
    window_border_color = '#252525'
    navbar_color = '#629ebb'
    controls_color = '#252525'
    border_offset = 0.1

    class syntax(CodeConfig.theme.syntax):
        color1 = '#629ebb'
        color2 = '#fd4f2a'
        color3 = '#fea027'
        color4 = '#93c47d'
        comment_color = '#999999'
        error_color = '#c27ba0'

    @property
    def top_padding(self) -> float:
        return super().top_padding + self.border_offset
    
    @property
    def text_offset(self) -> tuple[float, float]:
        right, down = super().text_offset
        return right - self.border_offset, down + self.border_offset
    
    def _draw(self, scene: CodeScene) -> None:
        super()._draw(scene)
        if self.animate:
            if self.border_offset:
                self._overflow_navbar = self._overflow_top.copy()
                self._overflow_navbar.set_fill(self.window_color)
                self._overflow_navbar.stretch(self.border_offset / self.config.height, dim=1)
                self._overflow_navbar.align_to(self._window, UL)
                scene.add(self._overflow_navbar)
                scene.play(
                    self._border.animate.shift(self.border_offset * DL),
                    self._navbar.animate.shift(self.border_offset * DL),
                    self._buttons.animate.shift(self.border_offset * DL),
                    run_time = 1,
                )
        else:
            if self.border_offset:
                self._border.shift(self.border_offset * DL)
                self._buttons.shift(self.border_offset * DL)
                self._navbar.shift(self.border_offset * DL)