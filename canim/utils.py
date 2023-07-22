from __future__ import annotations
from typing import Any

import datetime as dt
import inspect
import re


indent_regex = re.compile(r'^(\s*)(.*)$')


def log(message: str) -> None:
    print(f'[{dt.datetime.now()}] {message}')


def split_indent(string: str) -> tuple[str, str]:
    return indent_regex.match(string).groups()


def split_lines(string: str) -> list[str]:
    first_indent: int = None
    lines: list[str] = []
    for line in string.splitlines():
        whitespace, content = split_indent(line)
        if not content:
            continue
        if first_indent is None:
            first_indent = len(whitespace)
            lines.append(content)
        else:
            indent = len(whitespace) - first_indent
            lines.append(' ' * indent + content)
    return lines


class Config:

    def __init__(self, parent: Config = None, config_dict: dict[str, Any] = None, /, **config: Any):
        if config_dict is not None:
            config.update(config_dict)
        fields = {}
        for cls in self.__class__.__mro__:
            for key, value in cls.__dict__.items():
                if key in fields or key.startswith('_'):
                    continue
                if inspect.isclass(value):
                    fields[key] = value(self)
                elif not hasattr(value, '__get__'):
                    fields[key] = value
        for key, value in fields.items():
            setattr(self, key, value)
        self.update(config)
        self.parent = parent
    
    def __repr__(self):
        return f'<config {self.as_dict()!r}>'
    
    def update(self, config_dict: dict[str, Any] = None, /, **config: Any) -> None:
        if config_dict is not None:
            config.update(config_dict)
        for key, value in config.items():
            if '__' in key:
                key, subkey = key.split('__', 1)
                field = getattr(self, key)
                setattr(field, subkey, value)
            else:
                setattr(self, key, value)
                if isinstance(value, Config):
                    value.parent = self
    
    def as_dict(self) -> dict[str, Any]:
        return {key: value for key, value in self.__dict__.items() if key != 'parent'}