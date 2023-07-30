from canim import code_animation, CodeScene
from canim.themes import Window


@code_animation
def highlight_lines(scene: CodeScene):
    code = scene.code(small=True, style=Window())
    code >> '''
        Line 1
        Line 2
        Line 3
        Line 4
        Line 5
    '''
    with code[1:2, 4]:
       scene.wait(1)
    with code[2:4] * 'Line':
        scene.wait(1)
    scene.wait(1)