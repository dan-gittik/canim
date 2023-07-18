class CodeConfig:

    default_font = 'Monospace'
    default_font_size = 20
    default_line_gap = 0.25
    default_delay = 0.5

    def __init__(
            self,
            font: str = None,
            font_size: int = None,
            line_gap: float = None,
            delay: float = None,
            delay_before: float = None,
            delay_after: float = None,
    ):
        if font is None:
            font = self.default_font
        if font_size is None:
            font_size = self.default_font_size
        if line_gap is None:
            line_gap = self.default_line_gap
        if delay is None:
            delay = self.default_delay
        if delay_before is None:
            delay_before = delay
        if delay_after is None:
            delay_after = delay
        self.font = font
        self.font_size = font_size
        self.line_gap = line_gap
        self.delay = delay
        self.delay_before = delay_before
        self.delay_after = delay_after