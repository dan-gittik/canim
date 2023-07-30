from canim import code_animation, CodeScene
from canim.themes import Window


@code_animation
def scroll_into_view(scene: CodeScene):
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
    code >> '''
        Line 8
        Line 9
        Line 10
    '''
    code << 'Line 0'
    ~code[9]