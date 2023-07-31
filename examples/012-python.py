from canim import code_animation, CodeScene, themes


@code_animation
def example(scene: CodeScene):
    code = scene.code(language='python', prompts=['>>> ', '... '], theme=themes.Bauhaus())
    code >> '''
    >>> def inc x:
    ...     return x + 1
    >>> inc 1
    '''
    code(plain=True) >> '2'
    code(plain=True) >> '# This is a comment'
    code >> r'>>> print("1\n2\n3")'
    code >>= '''
    1
    2
    3
    '''