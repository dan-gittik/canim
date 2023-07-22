from canim import code_animation, CodeScene


@code_animation
def enclose(scene: CodeScene):
    code = scene.code(language='python')
    code >> '>>> x = 1 / 0'
    code[0](raw=True, at_once=True) // '''
        >>> try:
                {...}
        ... except Exception:
        ...     pass
    '''
    scene.wait(5)