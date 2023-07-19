from __future__ import annotations
from typing import Any, ContextManager

import contextlib
import re

from manim_voiceover import VoiceoverScene, VoiceoverTracker
from manim_voiceover.services.recorder import RecorderService


bookmark_regex = re.compile(r'\{(.*?)\}')


class CodeScene(VoiceoverScene):

    code_config: CodeConfig = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.code_config.voiceover:
            self.set_speech_service(RecorderService())

    def __repr__(self):
        return f'<code scene {self.__class__.__name__!r}>'

    def __matmul__(self, bookmark: Any) -> None:
        self.wait_until_bookmark(str(bookmark))

    def create_code_block(self, x: float, y: float) -> CodeBlock:
        return CodeBlock(self, x, y)
    
    @contextlib.contextmanager
    def voiceover(self, text: str) -> ContextManager[VoiceoverTracker]:
        text = bookmark_regex.sub(r'<bookmark mark="\1" />', text)
        with super().voiceover(text=text) as tracker:
            yield tracker


from .codeblock import CodeBlock
from .codeconfig import CodeConfig