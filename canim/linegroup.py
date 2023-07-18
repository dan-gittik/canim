from __future__ import annotations


class LineGroupSelector:

    def __init__(self, block: CodeBlock):
        self._block = block

    def __getitem__(self, selector: int|slice|tuple[int|slice]) -> LineGroup:
        if not isinstance(selector, tuple):
            selector = selector,
        lines = []
        for index in selector:
            if isinstance(index, int):
                lines.append(self._block._lines[index])
            else:
                lines.extend(self._block._lines[index])
        return LineGroup(self._block, lines)


class LineGroup:

    def __init__(self, block: CodeBlock, lines: list[CodeLine]):
        self._block = block
        self._lines = lines
    
    def remove(self) -> None:
        self._block.remove_lines(*self._lines)


from .codeblock import CodeBlock
from .codeline import CodeLine