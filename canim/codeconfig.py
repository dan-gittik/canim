from __future__ import annotations

import re

from .utils import Config


class CodeConfig(Config):
    debug = False
    small = False
    large_width = 12
    large_height = 6
    small_width = 8
    small_height = 4
    language: str = None
    prompts: list[str] = None
    default_indent: int = 4
    typing_speed = 0.1
    transition_speed = 0.5
    voiceover = False

    @property
    def width(self) -> float:
        return self.small_width if self.small else self.large_width

    @property
    def height(self) -> float:
        return self.small_height if self.small else self.large_height
    
    @property
    def prompt_pattern(self) -> str:
        if not self.prompts:
            return ''
        return '|'.join(re.escape(prompt) for prompt in self.prompts)

    class theme(Config):
        animate = True
        font = 'Monospace'
        font_size = 20
        font_color = '#000000'
        title_font = None
        title_size = None
        title_color = None
        paragraph_font = None
        paragraph_size = None
        paragraph_color = None
        line_gap = 0.25
        background_color = '#ffffff'
        window_color = '#ffffff'
        window_border_color = '#000000'
        window_border_width = 1
        window_padding = 0.25
        navbar_height = 0.5
        navbar_color = '#888888'
        controls_color = '#ffffff'
        dimmed_opacity = 0.25
        highlight_color = '#ffffaa'
        highlight_padding = 0.2
        z_index = 0
        text_z_index = 2
        z_range = 0

        @property
        def horizontal_padding(self) -> float:
            return 0
        
        @property
        def top_padding(self) -> float:
            return 0
        
        @property
        def bottom_padding(self) -> float:
            return 0
        
        @property
        def text_offset(self) -> tuple[float, float]:
            return 0, self.navbar_height

        def init(self, scene: CodeScene) -> None:
            if self.background_color:
                scene.camera.background_color = self.background_color
        
        def resize(self, scene: CodeScene) -> None:
            pass

        class syntax(Config):
            color1 = '#0000ff'
            color2 = '#00ff00'
            color3 = '#ffff00'
            color4 = ''
            comment_color = '#cccccc'
            error_color = '#ff0000'
            text = ''
            text_whitespace = ''
            comment = '{comment_color}'
            comment_preproc = ''
            comment_hashbang = ''
            comment_multiline = ''
            comment_preproc_file = ''
            comment_single = ''
            comment_special = ''
            keyword = '{color1} bold'
            keyword_pseudo = ''
            keyword_type = ''
            keyword_constant = '{color3} bold'
            keyword_declaration = ''
            keyword_namespace = ''
            keyword_reserved = ''
            operator = ''
            operator_word = ''
            name = ''
            name_builtin = '{color3} bold'
            name_function = 'bold'
            name_class = 'bold'
            name_namespace = 'bold'
            name_exception = 'bold'
            name_variable = ''
            name_constant = ''
            name_label = ''
            name_entity = ''
            name_attribute = ''
            name_tag = ''
            name_decorator = ''
            name_builtin_psuedo = ''
            name_function_magic = ''
            name_property = ''
            name_other = ''
            name_variable_class = ''
            name_variable_global = ''
            name_variable_magic = ''
            literal = '{color2}'
            literal_string = ''
            literal_string_doc = ''
            literal_string_interpol = ''
            literal_string_escape = ''
            literal_string_regex = ''
            literal_string_symbol = ''
            literal_string_other = ''
            literal_number = ''
            literal_date = ''
            literal_string_affix = ''
            literal_string_backtick = ''
            literal_string_char = ''
            literal_string_delimiter = ''
            literal_string_double = ''
            literal_string_heredoc = ''
            literal_strnig_single = ''
            literal_number_bin = ''
            literal_number_float = ''
            literal_number_hex = ''
            literal_number_integer = ''
            literal_number_integer_long = ''
            literal_number_oct = ''
            generic = ''
            generic_heading = ''
            generic_subheading = ''
            generic_deleted = ''
            generic_inserted = ''
            generic_error = '{error_color}'
            generic_emph = ''
            generic_strong = ''
            generic_prompt = ''
            generic_output = ''
            generic_traceback = '{error_color}'
            error = '{error_color}'
            escape = ''
            punctuation = ''
            punctuation_marker = ''
            other = ''


from .codescene import CodeScene