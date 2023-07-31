from canim import code_animation, CodeScene


@code_animation
def example(scene: CodeScene):
    code = scene.code()
    code >> '''
        Line 3
        Line 4
    '''
    code << '''
        Line 1
        Line 2
    '''