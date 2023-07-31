from canim import code_animation, CodeScene


@code_animation
def example(scene: CodeScene):
    code = scene.code()
    code >> 'Line 1'
    code >> 'Line 2g'
    code >> 'Line 3'