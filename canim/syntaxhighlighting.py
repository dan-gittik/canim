from __future__ import annotations
from typing import TextIO

from pygments import highlight
from pygments.lexers import get_lexer_by_name
from pygments.formatter import Formatter
from pygments.token import Token

from .utils import log


class SyntaxHighligher:

    def __init__(self, language: str, theme: CodeConfig.theme.syntax):
        self.language = language
        self._lexer = get_lexer_by_name(self.language)
        self._formatter = PangoFormatter(**theme.as_dict())
    
    def __repr__(self):
        return f'<syntax highlighter for {self.language}>'
    
    def highlight(self, text: str) -> str:
        return highlight(text, self._lexer, self._formatter)


class PangoFormatter(Formatter):

    value_attributes = dict(
        bold = 'weight',
        italic = 'style',
    )

    def __init__(self, debug: bool = False, **theme: str):
        super().__init__()
        self.debug = debug
        self.tags: dict[str, tuple[str, str]] = {}
        for token, option in theme.items():
            token = 'Token.' + '.'.join(word.capitalize() for word in token.split('_'))
            if not option:
                self.tags[token] = '', ''
                continue
            attributes = {}
            for value in option.format(**theme).split():
                if value.startswith('#'):
                    attributes['color'] = value
                elif value in self.value_attributes:
                    attributes[self.value_attributes[value]] = value
            attribute_list = ' '.join(f'{key}="{value}"' for key, value in attributes.items())
            self.tags[token] = f'<span {attribute_list}>', '</span>'

    def format(self, tokens: list[tuple[Token, str]], output: TextIO) -> None:
        last_token: str = None
        last_value = ''
        for token, value in tokens:
            token = str(token)
            if token == last_token:
                last_value += value
                continue
            output.write(self._entag(last_token, last_value))
            last_value = value
            last_token = token
        output.write(self._entag(last_token, last_value))
    
    def _entag(self, token: str, value: str) -> str:
        if not value:
            return ''
        start = end = ''
        if self.debug:
            log(f'considering {token} {value!r}')
        while '.' in token:
            start, end = self.tags[token]
            if start and end:
                log(f'matched {token} with tag {start}')
                break
            token = token.rsplit('.', 1)[0]
        log(f'no matching tag found')
        return start + value + end
    

from .codeconfig import CodeConfig