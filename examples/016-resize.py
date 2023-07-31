from canim import code_animation, CodeScene, themes


@code_animation
def example(scene: CodeScene):
    code = scene.code(small=True, theme=themes.Bauhaus())
    code >> '''
    Line 1
    Line 2
    Line 3
    '''
    code.resize()
    code >> '''
    Line 1
    Line 2
    Line 3
    '''
    code.resize()
    code >> '''
    Line 1
    Line 2
    Line 3
    '''