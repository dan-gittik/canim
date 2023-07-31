from canim import code_animation, CodeScene, themes


@code_animation
def example(scene: CodeScene):
    code = scene.code(language='python', prompts=['>>> ', '... '], theme=themes.Bauhaus())
    code >> '''
        >>> x = 1 / 0
        >>> print(x)
        >>> print(E)
    '''
    code[0] // '''
        >>> try:
        ...     {...}
        ... except Exception:
        ...     pass
    '''
    scene.wait(5)