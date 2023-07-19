class CodeConfig:

    default_font = 'Monospace'
    default_font_size = 20
    default_line_gap = 0.25
    default_typing_speed = 0.1
    default_slide_speed = 0.5
    default_voiceover = False

    def __init__(
            self,
            font: str = None,
            font_size: int = None,
            line_gap: float = None,
            typing_speed: float = None,
            slide_speed: float = None,
            voiceover: bool = None,
    ):
        if font is None:
            font = self.default_font
        if font_size is None:
            font_size = self.default_font_size
        if line_gap is None:
            line_gap = self.default_line_gap
        if typing_speed is None:
            typing_speed = self.default_typing_speed
        if slide_speed is None:
            slide_speed = self.default_slide_speed
        if voiceover is None:
            voiceover = self.default_voiceover
        self.font = font
        self.font_size = font_size
        self.line_gap = line_gap
        self.typing_speed = typing_speed
        self.slide_speed = slide_speed
        self.voiceover = voiceover