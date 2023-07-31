from __future__ import annotations
from typing import Any, ContextManager, Pattern

import contextlib
import collections
import re

from manim import (
    UL,
    LEFT,
    RIGHT,
    MarkupText,
    Rectangle,
    Animation,
    FadeOut,
    LaggedStart,
)
from manim_voiceover import VoiceoverTracker
from manim_voiceover.services.recorder import RecorderService

from .utils import split_lines


bookmark_regex = re.compile(r'\{(.*?)\}')


class CodeBlock:

    def __init__(self, scene: CodeScene, config: CodeConfig):
        self.scene = scene
        self.config = config
        self.lines: list[CodeLine] = []
        self._stash: dict[str, Any] = {}
        self._transitions: list[Animation] = []
        if config.language:
            self._syntax_highlighter = SyntaxHighligher(config.language, config.theme.syntax)
        else:
            self._syntax_highlighter = None
        self._font_alignment = FontAlignment(config.theme.font, config.theme.font_size)
        if self.config.voiceover:
            self.scene.set_speech_service(RecorderService())
        self.config.theme.init(self.scene)
    
    def __repr__(self):
        return f'<code block: {self.config}>'

    def __getitem__(self, selector: int|slice|tuple[int|slice]) -> CodeLineGroup:
        if not isinstance(selector, tuple):
            selector = selector,
        lines = []
        for index in selector:
            if isinstance(index, int):
                lines.append(self.lines[index])
            else:
                lines.extend(self.lines[index])
        return CodeLineGroup(self, lines)
    
    def __call__(self, **stash: Any) -> CodeBlock:
        self._stash = stash
        return self
    
    def __neg__(self) -> CodeBlock:
        self.clear(**self._stash)
        self._stash.clear()
        return self
    
    def __rshift__(self, string: str) -> list[CodeLine]:
        lines = self.append_lines(string, **self._stash)
        self._stash.clear()
        return lines
    
    def __lshift__(self, string: str) -> list[CodeLine]:
        lines = self.prepend_lines(string, **self._stash)
        self._stash.clear()
        return lines
    
    def __matmul__(self, bookmark: Any) -> CodeBlock:
        self.scene.wait_until_bookmark(str(bookmark))
        return self
    
    def __irshift__(self, string: str) -> CodeBlock:
        self.append_lines(string, plain=True)
        return self
    
    @contextlib.contextmanager
    def voiceover(self, text: str) -> ContextManager[VoiceoverTracker]:
        text = bookmark_regex.sub(r'<bookmark mark="\1" />', text)
        with self.scene.voiceover(text=text) as tracker:
            yield tracker
        
    @property
    def theme(self) -> CodeConfig.theme:
        return self.config.theme
    
    @property
    def top(self) -> float:
        return self.config.height / 2 - self.theme.top_padding
    
    @property
    def bottom(self) -> float:
        return -self.config.height / 2 + self.theme.bottom_padding
    
    @property
    def left(self):
        return -self.config.width / 2 + self.theme.horizontal_padding

    def scroll_into_view(self, first_line: CodeLine, last_line: CodeLine = None) -> None:
        scroll = self._find_scroll_for(first_line, last_line)
        self._animate_slide(scroll)
    
    def scroll_to_end(self, buffer: int) -> None:
        if not self.lines:
            return
        scroll = self._find_scroll_for(self.lines[-1])
        scroll -= (self._font_alignment.height + self.theme.line_gap) * buffer
        self._animate_slide(scroll)

    def insert_lines(
            self,
            index: int,
            *strings: str,
            indent_lines: int|CodeLineGroup|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        lines = self._create_lines(*strings, plain=plain)
        if not lines:
            return
        if index < 0:
            index = 0
        if index > len(self.lines):
            index = len(self.lines)
        indent_lines = self._resolve_lines(index, indent_lines)
        self._animate_insert(
            insertions = {index: lines},
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
        self._insert_lines(index, lines)
        return lines

    def prepend_lines(
            self,
            *strings: str,
            indent_lines: int|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.insert_lines(
            0,
            *strings,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
    
    def append_lines(
            self,
            *strings: str,
            indent_lines: int|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        return self.insert_lines(
            len(self.lines),
            *strings,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
    
    def remove_lines(
            self,
            lines: list[CodeLine],
            dedent_lines: int|CodeLineGroup|list[CodeLine],
            dedent_level: int = None,
            dedent_prompt: str = None,
    ) -> None:
        if not lines:
            return
        self._sort_lines(lines)
        index = lines[-1].index + 1
        dedent_lines = self._resolve_lines(index, dedent_lines)
        self._sort_lines(dedent_lines)
        self._animate_remove(
            lines = lines,
            dedent_lines = dedent_lines,
            dedent_level = dedent_level,
            dedent_prompt = dedent_prompt,
        )
        self._remove_lines(lines)
    
    def clear(self) -> None:
        self.remove_lines(self.lines)
    
    def replace_lines(
            self,
            lines: list[CodeLine],
            *strings: str,
            indent_lines: int|CodeLineGroup|list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        new_lines = self._create_lines(*strings, plain=plain)
        if not lines or not new_lines:
            return
        self._sort_lines(lines)
        index = lines[0].index
        indent_lines = self._resolve_lines(index, indent_lines)
        self._animate_insert(
            insertions = {index: new_lines},
            replace_lines = lines,
            indent_lines = indent_lines,
            indent_level = indent_level,
            indent_prompt = indent_prompt,
            plain = plain,
        )
        self._insert_lines(index, new_lines)
        self._remove_lines(lines)
        return new_lines
    
    def enclose_lines(
            self,
            lines: list[CodeLine],
            before: str,
            after: str,
            *,
            indent: int = None,
            prompt: str = None,
            plain: bool = None,
    ) -> list[CodeLine]:
        if not lines:
            return
        self._sort_lines(lines)
        before_index = lines[0].index
        before_lines = self._create_lines(before, plain=plain)
        after_index = lines[-1].index + 1
        after_lines = self._create_lines(after, plain=plain)
        new_lines = [*before_lines, *after_lines]
        self._animate_insert(
            insertions = {before_index: before_lines, after_index: after_lines},
            indent_lines = self.lines[before_index:after_index],
            indent_level = indent,
            indent_prompt = prompt,
            plain = plain,
        )
        self._insert_lines(before_index, before_lines)
        self._insert_lines(after_index, after_lines)
        return new_lines
    
    @contextlib.contextmanager
    def highlight_lines(self, lines: list[CodeLine]) -> None:
        if not lines:
            return
        self._sort_lines(lines)
        self.scroll_into_view(lines[0], lines[-1])
        other_lines = [line for line in self.lines if line not in lines]
        if other_lines:
            self._animate_opacity(self.theme.dimmed_opacity, other_lines)
        try:
            yield
        finally:
            self._animate_opacity(1, other_lines)
    
    @contextlib.contextmanager
    def highlight_pattern(self, pattern: str|Pattern, lines: list[CodeLine] = None) -> None:
        if not lines:
            lines = self.lines
        if isinstance(pattern, str):
            pattern = re.compile(pattern)
        with self._animate_highlights(pattern, lines):
            yield
        
    def _add_transition(self, transition: Animation) -> None:
        self._transitions.append(transition)
    
    def _play_transitions(self, lag=None) -> None:
        if not self._transitions:
            return
        if self.config.animation:
            run_time = self.config.transition_speed
        else:
            run_time = 0
        if lag:
            self.scene.play(LaggedStart(*self._transitions, lag_ratio=lag, run_time=run_time))
        else:
            self.scene.play(*self._transitions, run_time=run_time)
        self._transitions.clear()
        
    def _insert_lines(self, index: int, lines: list[CodeLine]) -> None:
        self.lines[index:index] = lines

    def _remove_lines(self, lines: list[CodeLine]) -> None:
        self.lines = [line for line in self.lines if line not in lines]
    
    def _create_text(self, content: str) -> MarkupText:
        text = MarkupText(
            text = content,
            font = self.theme.font,
            font_size = self.theme.font_size,
            color = self.theme.font_color,
        )
        text.z_index = self.theme.text_z_index
        return text

    def _create_lines(self, *strings: str, plain: bool = None) -> list[CodeLine]:
        lines: list[CodeLine] = []
        for string in strings:
            for line in split_lines(string):
                lines.append(CodeLine.parse(self, line, plain=plain))
        return lines
    
    def _sort_lines(self, lines: list[CodeLine]) -> None:
        lines.sort(key=lambda line: line.index)
    
    def _resolve_lines(self, index: int, lines: int|CodeLineGroup|list[CodeLine]) -> list[CodeLine]:
        if not lines:
            return []
        if isinstance(lines, int):
            lines = self.lines[index:index + lines]
        elif isinstance(lines, CodeLineGroup):
            lines = lines.lines
        self._sort_lines(lines)
        return lines

    def _position_lines(self, lines: list[CodeLine], index: int, offset: float) -> None:
        prev_line: CodeLine = None
        for line_index, line in enumerate(lines, index):
            if line_index == 0:
                if not self.lines:
                    line._position(self.top - offset, self.left)
                else:
                    first_line = self.lines[0]
                    line._position(first_line.top - offset, first_line.left)
            else:
                if prev_line is None:
                    prev_line = self.lines[line_index - 1]
                line._position(prev_line.bottom - offset, prev_line.left)
            prev_line = line
            offset = 0
  
    def _find_scroll_for(self, first_line: CodeLine, last_line: CodeLine = None) -> float:
        if last_line is None:
            last_line = first_line
        threshold = first_line.height / 2
        if first_line.top > self.top + threshold:
            return first_line.top - self.top
        if last_line.bottom < self.bottom - threshold:
            return -(self.bottom - last_line.bottom)
        return 0

    def _animate_slide(self, offset: float, lines: list[CodeLine] = None) -> None:
        if lines is None:
            lines = self.lines
        if not offset or not lines:
            return
        for line in lines:
            line._animate_slide(offset)
        self._play_transitions()

    def _animate_insert(
            self,
            insertions: dict[int, list[CodeLine]],
            replace_lines: list[CodeLine] = None,
            indent_lines: list[CodeLine] = None,
            indent_level: int = None,
            indent_prompt: str = None,
            plain: bool = None,
    ) -> None:
        if replace_lines is None:
            replace_lines = []
        if indent_lines is None:
            indent_lines = []
        if indent_level is None:
            indent_level = self.config.default_indent
        all_new_lines: list[CodeLine] = []
        offsets: dict[CodeLine, float] = collections.defaultdict(float)
        replace_with: dict[CodeLine, CodeLine] = dict.fromkeys(replace_lines)
        first_index: int = None
        offset = 0.0
        for index, new_lines in sorted(insertions.items()):
            self._position_lines(new_lines, index, offset)
            if first_index is None:
                first_index = index
                scroll = self._find_scroll_for(new_lines[0], new_lines[-1])
                self._animate_slide(scroll)
                for new_line in new_lines:
                    new_line._slide(scroll)
            for old_line, new_line in zip(self.lines[index:], new_lines):
                if old_line not in replace_lines:
                    break
                replace_with[old_line] = new_line
                offset -= old_line.height
            offsets[index] = sum(new_line.height for new_line in new_lines)
            offset += offsets[index]
            all_new_lines.extend(new_lines)
        offset = 0.0
        for index, line in enumerate(self.lines[first_index:], first_index):
            offset += offsets.get(index, 0)
            if line in replace_lines:
                line._animate_remove(replace_with=replace_with[line])
                offset -= line.height
                continue
            if line in indent_lines:
                indent, prompt = indent_level, indent_prompt
            else:
                indent, prompt = None, None
            line._animate_slide(offset, indent=indent, prompt=prompt)
        self._play_transitions()
        for line in all_new_lines:
            line._animate_insert(plain=plain)
        self._play_transitions()
    
    def _animate_remove(
            self,
            lines: list[CodeLine],
            dedent_lines: list[CodeLine] = None,
            dedent_level: int = None,
            dedent_prompt: str = None,
    ) -> None:
        print(dedent_lines)
        if dedent_lines is None:
            dedent_lines = []
        if dedent_level is None:
            indent_level = -self.config.default_indent
        else:
            indent_level = -dedent_level
        offset = 0.0
        for line in self.lines:
            if line in lines:
                offset -= line.height
                line._animate_remove()
                continue
            if line in dedent_lines:
                indent, prompt = indent_level, dedent_prompt
            else:
                indent = prompt = None
            line._animate_slide(offset, indent=indent, prompt=prompt)
        self._play_transitions()

    def _animate_opacity(self, opacity: float, lines: list[CodeLine] = None) -> None:
        if not lines:
            lines = self.lines
        for line in lines:
            line._animate_opacity(opacity)
        self._play_transitions()
    
    @contextlib.contextmanager
    def _animate_highlights(self, pattern: Pattern, lines: list[CodeLine]) -> ContextManager[None]:
        highlights: list[Rectangle] = []
        for line in lines:
            for match in pattern.finditer(line.content):
                start, end = match.start(), match.end()
                highlight = Rectangle(
                    height = line.height + - self.theme.line_gap + self.theme.highlight_padding,
                    width = 0.01,
                    fill_color = self.theme.highlight_color,
                    fill_opacity = 1,
                )
                highlight.move_to([line.left, line.top + self.theme.highlight_padding / 2, 0], UL)
                highlight.shift((start - 0.5) * self._font_alignment.space_width * RIGHT)
                self.scene.add(highlight)
                self._add_transition(highlight.animate.stretch_to_fit_width((end - start + 1) * self._font_alignment.space_width, about_edge=LEFT))
                highlights.append(highlight)
        self._play_transitions(lag=0.2)
        try:
            yield
        finally:
            for highlight in highlights:
                self._add_transition(FadeOut(highlight))
            self._play_transitions()


from .codeconfig import CodeConfig
from .codeline import CodeLine, CodeLineGroup
from .codescene import CodeScene
from .fontalignment import FontAlignment
from .syntaxhighlighter import SyntaxHighligher