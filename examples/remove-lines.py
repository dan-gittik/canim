from canim import code_animation, CodeScene


@code_animation
def remove_lines(scene: CodeScene):
    code = scene.code()
    line1, *_ = code >> '''
        Line 1
        Line 2
        Line 3
        Line 4
        Line 5
        Line 6
    '''
    -line1
    -code[0:1, 3]