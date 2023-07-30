from canim import code_animation, CodeScene
from canim.themes import Bauhaus


@code_animation
def python(scene: CodeScene):
    code = scene.code(language='Python', style=Bauhaus())
    code >> '''
    >>> def inc(x):
    ...     return x + 1
    >>> inc(1)
    '''
    code(raw=True, at_once=True) >> '2'
    code(raw=True) >> '# This is a comment'
    code >> r'>>> print("1\n2\n3")'
    code >>= '''
    1
    2
    3
    '''