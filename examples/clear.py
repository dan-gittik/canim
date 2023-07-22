from canim import code_animation, CodeScene


@code_animation
def clear(scene: CodeScene):
    code = scene.code()
    code >> '''
    Line 1
    Line 2
    Line 3
    '''
    code.clear()
    code >> '''
    Line 1
    Line 2
    '''