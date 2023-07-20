from canim import code_animation, CodeScene


@code_animation
def slide_down(scene: CodeScene):
    code = scene.code()
    code >> 'Line 1'
    line4, = code >> 'Line 4'
    line2, = line4 << 'Line 2'
    line3, = code[2] << 'Line 3'
    code << 'Line 0'