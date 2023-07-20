from __future__ import annotations

from .utils import Config


class CodeConfig(Config):
    small = False
    large_width = 12
    large_height = 6
    small_width = 8
    small_height = 4
    typing_speed = 0.1
    slide_speed = 0.5
    voiceover = False

    @property
    def width(self) -> float:
        return self.small_width if self.small else self.large_width

    @property
    def height(self) -> float:
        return self.small_height if self.small else self.large_height

    class style(Config):
        font = 'Monospace'
        font_size = 20
        font_color = '#000000'
        line_gap = 0.25
        background_color = '#ffffff'
        window_color = '#ffffff'
        window_border_color = '#000000'
        window_border_width = 1
        window_padding = 0.25
        navbar_height = 0.5
        navbar_color = '#888888'
        controls_color = '#ffffff'

        @property
        def horizontal_padding(self) -> float:
            return 0
        
        @property
        def top_padding(self) -> float:
            return 0
        
        @property
        def bottom_padding(self) -> float:
            return 0

        def initialize(self, scene: CodeScene, animate: bool):
            pass
    

from .codescene import CodeScene