import re


indent_regex = re.compile(r'^(\s*)(.*)$')


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