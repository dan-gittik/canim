from canim import code_animation, CodeScene


@code_animation
def three(scene: CodeScene):
    code = scene(-6, 3)
    code >> 'Line 1'
    code >> 'Line 2'
    code >> 'Line 3'