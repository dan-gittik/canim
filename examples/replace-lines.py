from canim import code_animation, CodeScene
from canim.styles import Window


@code_animation
def replace_lines(scene: CodeScene):
    code = scene.code(small=True, style=Window())
    code >> '''
        Line 1
        Line 2
        Line 3
        Line 4
        Line 5
        Line 6
        Line 7
    '''
    code[1:3, 5] < '''
        New line 2
        New line 3
    '''