from canim import code_animation, CodeScene
from canim.styles import Window

from manim import UP


@code_animation
def window(scene: CodeScene):
    code = scene.code(small=True, style=Window(background_color='#cccccc'), animate=True)
    print(code.style.font_size)
    lines = code >> '''
        Line 1
        Line 2
        Line 3
        Line 4
        Line 5
        Line 6
        Line 7
        Line 8
        Line 9
        Line 10
    '''
    scene.play(*[line._mobject.animate.shift(UP * 2) for line in lines]) # Hacky test before scroll into view is automatic.