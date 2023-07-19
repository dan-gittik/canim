from canim import code_animation, CodeScene


@code_animation
def multiple_lines(scene: CodeScene):
    code = scene(-6, 3)
    code >> '''
        Line 3
        Line 4
    '''
    code << '''
        Line 1
        Line 2
    '''